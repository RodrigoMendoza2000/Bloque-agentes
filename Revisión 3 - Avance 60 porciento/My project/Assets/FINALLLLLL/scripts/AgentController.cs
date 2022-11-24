using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;

[Serializable]
public class AgentData
{
    public string id;
    public float x, y, z;
    public bool visible;

    public AgentData(string id, float x, float y, float z, bool visible)
    {
        this.id = id;
        this.x = x;
        this.y = y;
        this.z = z;
        this.visible = visible;
    }
}


[Serializable]
public class AgentsData
{
    public List<AgentData> agents;

    public AgentsData() => this.agents = new List<AgentData>();
}




public class AgentController : MonoBehaviour
{
    // Ruta de la nube
    // private string url = "https://agents.us-south.cf.appdomain.cloud/";
    string serverUrl = "http://localhost:8585";
    // Endpoints (que coincidan nombres)
    string getAgentsEndpoint = "/getAgents";
    string getObstaclesEndpoint = "/getObstacles";
    string getStateEndpoint = "/getState";
    string sendConfigEndpoint = "/init";
    string updateEndpoint = "/update";

    AgentsData agentsData, obstacleData;
    Dictionary<string, AgentData>  agentsDict = new Dictionary<string, AgentData>();
    Dictionary<string, GameObject> agents;
    Dictionary<string, Vector3> prevPositions, currPositions;
    HashSet<string> idCars = new HashSet<string>();

    bool update_a = false, started_a = false;
    bool update_b = false, started_b = false;

    // Una celda es una unidad de Unity
    public GameObject agentPrefab, obstaclePrefab;
    public int N, max_steps;
    public float timeToUpdate = 5.0f;
    private float timer, dt;

    void Start()
    {

        // Creación de objetos base
        agentsData = new AgentsData();
        obstacleData = new AgentsData();

        prevPositions = new Dictionary<string, Vector3>();
        currPositions = new Dictionary<string, Vector3>();


        agents = new Dictionary<string, GameObject>();

        timer = timeToUpdate;

        // Permite iniciar una función que corre de manera concurrente (mismo tiempo que la principal)
        StartCoroutine(SendConfiguration());
    }

    private void Update()
    {   // Sirve para hacer solicitud de nuevas posiciones
        if (timer < 0)
            {
                timer = timeToUpdate;
                update_a = false;
                update_b = true;
                StartCoroutine(UpdateSimulation());
            }
        // Si ya actualicé posiciones de mis agentes
        if (update_a)
        {
            timer -= Time.deltaTime;
            dt = 1.0f - (timer / timeToUpdate);

            float ndt = dt * dt * (3 - 2 * dt);
            Debug.Log(currPositions.Count);
            foreach (var agent in currPositions)
            {
                Debug.Log(agent.Key);
                Vector3 currentPosition = agent.Value;
                Vector3 previousPosition = prevPositions[agent.Key];
                // Interpolación lineal para que se mueva poco a poco hasta la dirección final

                Vector3 interpolated = Vector3.Lerp(previousPosition, currentPosition, dt);
                // Resta de vectores
                Vector3 direction = currentPosition - interpolated;

                agents[agent.Key].transform.localPosition = interpolated;

                if (agent.Key[0] == '1')
                {
                   if (direction != Vector3.zero) agents[agent.Key].transform.rotation = Quaternion.LookRotation(direction);
                }
            }
            // Interpolación
            // float t = (timer / timeToUpdate);
            // dt = t * t * ( 3f - 2f*t);
        }


    }

    IEnumerator UpdateSimulation()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + updateEndpoint);
        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else
        {
            StartCoroutine(GetAgentsData());
            //StartCoroutine(GetObstacleData());

        }
    }

    // Configuración inicial se pone en el editor de unity y se manda a flask
    IEnumerator SendConfiguration()
    {
        // Se manda la info a través de una forma
        WWWForm form = new WWWForm();

        // deben llamarse igual. Salen del editor de Unity. En mesa deben llamarse como el String
        form.AddField("N", N.ToString());

        // Se manda un post
        UnityWebRequest www = UnityWebRequest.Post(serverUrl + sendConfigEndpoint, form);
        www.SetRequestHeader("Content-Type", "application/x-www-form-urlencoded");

        //Aquí manda el web request
        yield return www.SendWebRequest();
        //Aquí ya terminó la corutina
        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(www.error);
        }
        else
        {
            // se mandan 2 co-rutinas
            Debug.Log("Configuration upload complete!");
            Debug.Log("Getting Agents positions");
            StartCoroutine(GetAgentsData());
            //StartCoroutine(GetObstacleData());

        }
    }


    IEnumerator GetAgentsData()
    {   //obtener nuevas posiciones de los agentes
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getAgentsEndpoint);
        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else
        {
            agentsData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);

            foreach (AgentData agent in agentsData.agents)
            {
                Vector3 newagentPosition = new Vector3(agent.x, agent.y, agent.z);

                GameObject agentobject;
                if (!agents.TryGetValue(agent.id, out agentobject))
                //if(started_a)
                //if (!idcars.contains(agent.key))
                {
                    // si es la primera vez que se ejecuta
                    prevPositions[agent.id] = newagentPosition;
                    //guarda referencia al agente nuevo en la posicion inicial 
                    agents[agent.id] = Instantiate(agentPrefab, newagentPosition, Quaternion.identity);
                    idCars.Add(agent.id);
                }
                else
                {   // no es la 1ª vez
                    Vector3 currentPosition = new Vector3();
                    if (currPositions.TryGetValue(agent.id, out currentPosition))
                        prevPositions[agent.id] = currentPosition;
                    currPositions[agent.id] = newagentPosition;
                }
            }
            if (agents.Count == N)
            {
                started_a = true;
            }
            update_a = true;
        }
    }


    //IEnumerator GetObstacleData()
    //{
    //    // Posiciones de los agentes obstáculos
    //    UnityWebRequest www = UnityWebRequest.Get(serverUrl + getObstaclesEndpoint);
    //    yield return www.SendWebRequest();

    //    if (www.result != UnityWebRequest.Result.Success)
    //        Debug.Log(www.error);
    //    else
    //    {
    //        Debug.Log(www.downloadHandler.text);
    //        obstacleData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);

    //        //Debug.Log(obstacleData.positions);
    //        //Debug.Log(www.downloadHandler.text);

    //        foreach (AgentData obstacle in obstacleData.agents.Values)
    //        {
    //            // Crear los prefabs. Agregar objetos nuevos a Unity

    //            Vector3 newAgentPosition = new Vector3(obstacle.x, obstacle.y, obstacle.z);

    //            if (!started_b)
    //            {   // si es la primera vez que se ejecuta
    //                prevPositions[obstacle.id] = newAgentPosition;
    //                //guarda referencia al agente nuevo en la posicion inicial 
    //                agents[obstacle.id] = Instantiate(obstaclePrefab, new Vector3(obstacle.x, obstacle.y, obstacle.z), Quaternion.identity);
    //            }
    //            else
    //            {   // no es la 1ª vez
    //                Vector3 currentPosition = new Vector3();
    //                if (currPositions.TryGetValue(obstacle.id, out currentPosition))
    //                    prevPositions[obstacle.id] = currentPosition;
    //                currPositions[obstacle.id] = newAgentPosition;
    //            }
    //        }
    //        update_b = true;
    //        if (!started_b) started_b = true;
    //    }
    //}
}


