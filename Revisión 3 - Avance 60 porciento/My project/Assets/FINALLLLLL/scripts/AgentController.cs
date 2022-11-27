using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;

public class CarData
{
    public float x, y, z;
    public List<int> destination;
    public bool turning;
    public int stopsTurning = 1;
    public bool parking;
    public bool draw = false;

    public CarData(float x = 0, float y = 0, float z = 0, List<int> destination = null, bool turning = false, bool parking = false)
    {
        this.x = x;
        this.y = y;
        this.z = z;
        this.destination = destination;
        this.turning = turning;
        this.parking = parking;
    }
}

public class PersonData
{
    public float x, y, z;
    public Vector3 offset = new Vector3(UnityEngine.Random.Range(-0.4f, 0.4f), 0, UnityEngine.Random.Range(-0.35f, 0.35f));
    public bool inBus;
    public int showInBus = 1;

    public PersonData(float x = 0, float y = 0, float z = 0, bool inBus = false)
    {
        this.x = x;
        this.y = y;
        this.z = z;
        this.inBus = inBus;
    }
}


[Serializable]
public class AgentsData
{
    [Serializable]
    public class WebCarData
    {
        public string id;
        public float x, y, z;
        public List<int> destination;
        public bool turning;
        public bool parking;

        public WebCarData(string id, float x, float y, float z, List<int> destination, bool turning, bool parking)
        {
            this.id = id;
            this.x = x;
            this.y = y;
            this.z = z;
            this.destination = destination;
            this.turning = turning;
            this.parking = parking;
        }
    }

    [Serializable]
    public class WebPersonData
    {
        public string id;
        public float x, y, z;
        public bool inBus;

        public WebPersonData(string id, float x, float y, float z, bool inBus)
        {
            this.id = id;
            this.x = x;
            this.y = y;
            this.z = z;
            this.inBus = inBus;
        }
    }

    public List<WebCarData> cars;
    public BusData bus;
    public List<WebPersonData> people;

    public AgentsData()
    {
        this.cars = new List<WebCarData>();
        this.bus = new BusData();
        this.people = new List<WebPersonData>();
    }

    public void UpdateCarsDict(Dictionary<string, CarData> dict)
    {
        foreach (WebCarData agent in cars)
        {
            dict[agent.id].x = agent.x;
            dict[agent.id].y = agent.y;
            dict[agent.id].z = agent.z;
            dict[agent.id].destination = agent.destination;
            dict[agent.id].turning = agent.turning;
            dict[agent.id].parking = agent.parking;
        }
    }

    public void UpdatePeopleDict(Dictionary<string, PersonData> dict)
    {
        foreach (WebPersonData agent in people)
        {
            dict[agent.id].x = agent.x;
            dict[agent.id].y = agent.y;
            dict[agent.id].z = agent.z;
            if (agent.inBus && dict[agent.id].showInBus > 0)
            {
                dict[agent.id].inBus = false;
                dict[agent.id].showInBus -= 1;
            }
            else if (!agent.inBus)
            {
                dict[agent.id].showInBus = 1;
                dict[agent.id].inBus = agent.inBus;
            }
            else
            {
                dict[agent.id].inBus = agent.inBus;
            }
        }
    }
}

[Serializable]
public class BusData
{
    public float x, y, z;

    public BusData(float x = 0, float y = 0, float z = 0)
    {
        this.x = x;
        this.y = y;
        this.z = z;
    }
}


public class AgentController : MonoBehaviour
{
    // Ruta de la nube
    // private string url = "https://agents.us-south.cf.appdomain.cloud/";
    string serverUrl = "http://localhost:8585";
    // Endpoints (que coincidan nombres)
    string getAgentsEndpoint = "/getAgents";
    string sendConfigEndpoint = "/init";
    string updateEndpoint = "/update";

    AgentsData agentsData;
    Dictionary<string, CarData>  carsDict = new Dictionary<string, CarData>();
    Dictionary<string, PersonData> peopleDict = new Dictionary<string, PersonData>();
    Dictionary<string, GameObject> agentsObject;
    Dictionary<string, Vector3> prevPositions, currPositions;
    HashSet<string> idAgents = new HashSet<string>();

    bool update_a = false, started_a = false;

    // Una celda es una unidad de Unity
    public GameObject carPrefab, busPrefab, personPrefab;
    public int N, max_steps;
    public float timeToUpdate = 5.0f;
    private float timer, dt;

    void Start()
    {

        // Creación de objetos base
        agentsData = new AgentsData();

        prevPositions = new Dictionary<string, Vector3>();
        currPositions = new Dictionary<string, Vector3>();

        for (int i = 0; i < N; i++)
        {
            carsDict['c' + i.ToString()] = new CarData();
        }

        for (int i = 0; i < 25; i ++)
        {
            peopleDict['p' + i.ToString()] = new PersonData();
        }


        agentsObject = new Dictionary<string, GameObject>();

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
                StartCoroutine(UpdateSimulation());
            }
        // Si ya actualicé posiciones de mis agentes
        if (update_a)
        {
            timer -= Time.deltaTime;
            dt = 1.0f - (timer / timeToUpdate);

            float ndt = dt * dt * (3 - 2 * dt);

            foreach (var agent in currPositions)
            {
                if (agent.Key[0] == 'c')
                {
                    if (carsDict[agent.Key].destination != null && carsDict[agent.Key].destination.Count > 0)
                    {
                        agentsObject[agent.Key].SetActive(true);
                    }
                    if (carsDict[agent.Key].parking)
                    {
                        agentsObject[agent.Key].SetActive(false);
                    }

                    if (carsDict[agent.Key].turning)
                    {
                        agentsObject[agent.Key].GetComponent<Renderer>().material.color = new Color(255, 0, 0);
                    } 
                    else
                    {
                        agentsObject[agent.Key].GetComponent<Renderer>().material.color = new Color(0, 0, 255);
                    }
                }

                Vector3 currentPosition = agent.Value;
                Vector3 previousPosition = prevPositions[agent.Key];
                // Interpolación lineal para que se mueva poco a poco hasta la dirección final

                Vector3 interpolated = Vector3.Lerp(previousPosition, currentPosition, dt);
                // Resta de vectores
                Vector3 direction = currentPosition - interpolated;

                if (agent.Key[0] == 'p')
                {
                    agentsObject[agent.Key].transform.localPosition = interpolated + peopleDict[agent.Key].offset;
                    if (peopleDict[agent.Key].inBus)
                    {
                        agentsObject[agent.Key].SetActive(false);
                    }
                    else
                    {
                        agentsObject[agent.Key].SetActive(true);
                    }

                }
                else
                {
                    agentsObject[agent.Key].transform.localPosition = interpolated;
                }

                if (agent.Key[0] == 'c' || agent.Key[0] == 'b' || agent.Key[0] == 'p')
                {
                    if (direction != Vector3.zero) agentsObject[agent.Key].transform.rotation = Quaternion.LookRotation(direction);
                }

            }
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
            agentsData.UpdateCarsDict(carsDict);
            agentsData.UpdatePeopleDict(peopleDict);

            // Update cars positions
            foreach (var car in carsDict)
            {
                Vector3 newagentPosition = new Vector3(car.Value.x, car.Value.y, car.Value.z);
                UpdatePosition(car.Key, newagentPosition);
            }

            // Update bus position
            Vector3 newBusPosition = new Vector3(agentsData.bus.x, agentsData.bus.y, agentsData.bus.z);
            UpdatePosition("b1", newBusPosition);
            
            // u
            foreach (var person in peopleDict)
            {
                Vector3 newagentPosition = new Vector3(person.Value.x, person.Value.y, person.Value.z);
                UpdatePosition(person.Key, newagentPosition);
            }


            if (agentsObject.Count == N)
            {
                started_a = true;
            }
            update_a = true;
        }
    }

    void UpdatePosition(string id, Vector3 newPos)
    {
        if (!idAgents.Contains(id))
        {
            // si es la primera vez que se ejecuta
            prevPositions[id] = newPos;
            //guarda referencia al agente nuevo en la posicion inicial 
            if (id[0] == 'c')
            {
                agentsObject[id] = Instantiate(carPrefab, newPos, Quaternion.identity);
                agentsObject[id].SetActive(false);
            }
            else if (id[0] == 'b')
            {
                agentsObject[id] = Instantiate(busPrefab, newPos, Quaternion.identity);
                agentsObject[id].SetActive(true);
            }
            else
            {
                agentsObject[id] = Instantiate(personPrefab, newPos, Quaternion.identity);
                agentsObject[id].SetActive(true);
            }


            idAgents.Add(id);
        }
        else
        {   // no es la 1ª vez
            Vector3 currentPosition = new Vector3();
            if (currPositions.TryGetValue(id, out currentPosition))
            {
                prevPositions[id] = currentPosition;
            }
            currPositions[id] = newPos;
        }
    }

}


