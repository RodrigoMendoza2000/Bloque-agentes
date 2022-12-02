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
    public Vector3 offset = new Vector3(UnityEngine.Random.Range(-0.4f, 0.4f), 0.12f, UnityEngine.Random.Range(-0.35f, 0.35f));
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
public class TrafficLightsData
{
    public string id;
    public bool state;

    public TrafficLightsData(string id, bool state)
    {
        this.id = id;
        this.state = state;
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
    public List<TrafficLightsData> trafficLights;

    public AgentsData()
    {
        this.cars = new List<WebCarData>();
        this.bus = new BusData();
        this.people = new List<WebPersonData>();
        this.trafficLights = new List<TrafficLightsData>();
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
    System.Random random = new System.Random();

    // URL
    string serverUrl = "http://localhost:8585";

    // Endpoints
    string getAgentsEndpoint = "/getAgents";
    string sendConfigEndpoint = "/init";
    string updateEndpoint = "/update";

    // Agents data
    AgentsData agentsData;
    Dictionary<string, CarData> carsDict = new Dictionary<string, CarData>();
    Dictionary<string, PersonData> peopleDict = new Dictionary<string, PersonData>();
    // Agents objects
    Dictionary<string, GameObject> agentsObject;
    // Agents positions
    Dictionary<string, Vector3> prevPositions, currPositions;
    // Active agents
    HashSet<string> idAgents = new HashSet<string>();

    bool update_a = false;

    // Dynamic prefabs
    public GameObject carPrefabA, carPrefabB, carPrefabC, carPrefabD;
    public GameObject busPrefab, personPrefab;
    // Simulation varialbes
    public int N, max_steps;
    public float timeToUpdate = 5.0f;
    private float timer, dt;

    void Start()
    {
        // Creaci?n de objetos base
        agentsData = new AgentsData();

        prevPositions = new Dictionary<string, Vector3>();
        currPositions = new Dictionary<string, Vector3>();

        for (int i = 0; i < N; i++)
        {
            carsDict['c' + i.ToString()] = new CarData();
        }

        for (int i = 0; i < 25; i++)
        {
            peopleDict['p' + i.ToString()] = new PersonData();
        }


        agentsObject = new Dictionary<string, GameObject>();

        agentsObject["tl581"] = GameObject.Find("tl581");
        agentsObject["tl534"] = GameObject.Find("tl534");
        agentsObject["tl541"] = GameObject.Find("tl541");
        agentsObject["tl588"] = GameObject.Find("tl588");
        agentsObject["tl430"] = GameObject.Find("tl430");
        agentsObject["tl405"] = GameObject.Find("tl405");
        agentsObject["tl198"] = GameObject.Find("tl198");
        agentsObject["tl152"] = GameObject.Find("tl152");
        agentsObject["tl290"] = GameObject.Find("tl290");
        agentsObject["tl265"] = GameObject.Find("tl265");
        agentsObject["tl64"] = GameObject.Find("tl64");
        agentsObject["tl18"] = GameObject.Find("tl18");

        timer = timeToUpdate;

        
        StartCoroutine(SendConfiguration());
    }

    private void Update()
    {   // Ask for new positions
        if (timer < 0)
        {
            timer = timeToUpdate;
            update_a = false;
            StartCoroutine(UpdateSimulation());
        }
        // If positions are updated
        if (update_a)
        {
            timer -= Time.deltaTime;
            dt = 1.0f - (timer / timeToUpdate);

            // Update agents
            foreach (var agent in currPositions)
            {
                // Updat position (linear interpolation)
                Vector3 currentPosition = agent.Value;
                Vector3 previousPosition = prevPositions[agent.Key];
                Vector3 interpolated = Vector3.Lerp(previousPosition, currentPosition, dt);
                Vector3 direction = currentPosition - interpolated;

                // Update direction
                if (agent.Key[0] == 'c' || agent.Key[0] == 'b' || agent.Key[0] == 'p')
                {
                    if (direction != Vector3.zero) agentsObject[agent.Key].transform.rotation = Quaternion.LookRotation(direction);
                }

                // Car
                if (agent.Key[0] == 'c')
                {
                    // Show object if needed
                    if (carsDict[agent.Key].destination != null && carsDict[agent.Key].destination.Count > 0)
                    {
                        agentsObject[agent.Key].SetActive(true);
                    }
                    if (carsDict[agent.Key].parking)
                    {
                        agentsObject[agent.Key].SetActive(false);
                    }
                }

                // Person
                if (agent.Key[0] == 'p')
                {
                    // Move and offset person position
                    agentsObject[agent.Key].transform.localPosition = interpolated + peopleDict[agent.Key].offset;
                    // Show object if needed
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
                    // Move object
                    agentsObject[agent.Key].transform.localPosition = interpolated;
                }

                // Traffic Lights
                foreach (var trafficLightD in agentsData.trafficLights)
                {
                    GameObject trafficL;
                    if (agentsObject.TryGetValue(trafficLightD.id, out trafficL))
                    {
 
                        GameObject green = trafficL.transform.Find("Green").gameObject;
                        GameObject red = trafficL.transform.Find("Red").gameObject;
                        if (trafficLightD.state)
                        {
                            green.SetActive(true);
                            red.SetActive(false);
                        }
                        else
                        {
                            green.SetActive(false);
                            red.SetActive(true);
                        }
                      
                    }
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
        }
    }

    IEnumerator SendConfiguration()
    {
        WWWForm form = new WWWForm();

        form.AddField("N", N.ToString());

        UnityWebRequest www = UnityWebRequest.Post(serverUrl + sendConfigEndpoint, form);
        www.SetRequestHeader("Content-Type", "application/x-www-form-urlencoded");

        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(www.error);
        }
        else
        {

            Debug.Log("Configuration upload complete!");
            Debug.Log("Getting Agents positions");
            StartCoroutine(GetAgentsData());
        }
    }


    IEnumerator GetAgentsData()
    {
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

            // Update people positions
            foreach (var person in peopleDict)
            {
                Vector3 newagentPosition = new Vector3(person.Value.x, person.Value.y, person.Value.z);
                UpdatePosition(person.Key, newagentPosition);
            }


            update_a = true;
        }
    }

    void UpdatePosition(string id, Vector3 newPos)
    {
        // New agent
        if (!idAgents.Contains(id))
        {
            prevPositions[id] = newPos;
            if (id[0] == 'c')
            {
                int n = random.Next(4);
                GameObject prefab;
                switch (n)
                {
                    case 0:
                        prefab = carPrefabA;
                        break;
                    case 1:
                        prefab = carPrefabB;
                        break;
                    case 2:
                        prefab = carPrefabC;
                        break;
                    default:
                        prefab = carPrefabD;
                        break;
                }

                agentsObject[id] = Instantiate(prefab, newPos, Quaternion.identity);
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
        // Existing agent
        else
        {   // no es la 1? vez
            Vector3 currentPosition = new Vector3();
            if (currPositions.TryGetValue(id, out currentPosition))
            {
                prevPositions[id] = currentPosition;
            }
            currPositions[id] = newPos;
        }
    }

}