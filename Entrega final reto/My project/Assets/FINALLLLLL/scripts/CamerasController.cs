using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CamerasController : MonoBehaviour
{
    public Camera sideTopCam;
    public Camera topCam;
    public Camera busCam;
    public Camera trafficLightCam;
    public Camera roundaboutCam;
    public Camera parkingLotCam;
    // Start is called before the first frame update
    void Start()
    {
        sideTopCam.enabled = true;
        sideTopCam.tag = "MainCamera";

        topCam.enabled = false;
        topCam.tag = "Untagged";

        busCam.enabled = false;
        busCam.tag = "Untagged";

        trafficLightCam.enabled = false;
        trafficLightCam.tag = "Untagged";

        roundaboutCam.enabled = false;
        roundaboutCam.tag = "Untagged";

        parkingLotCam.enabled = false;
        parkingLotCam.tag = "Untagged";
    }

    // Update is called once per frame
    void Update()
    {
        if (Input.GetKeyDown("1"))
        {
            // Al inicio está activa SIDE TOP CAMERA
            sideTopCam.enabled = true;
            sideTopCam.tag = "MainCamera";

            topCam.enabled = false;
            busCam.enabled = false;
            trafficLightCam.enabled = false;
            roundaboutCam.enabled = false;
            parkingLotCam.enabled = false;
        }
        else if (Input.GetKeyDown("3"))
        {
            // BUS CAMERA
            busCam.enabled = true;
            busCam.tag = "MainCamera";

            sideTopCam.enabled = false;
            topCam.enabled = false;
            trafficLightCam.enabled = false;
            roundaboutCam.enabled = false;
            parkingLotCam.enabled = false;

        }
        else if (Input.GetKeyDown("2"))
        {
            // ROUNDABOUT CAMERA
            roundaboutCam.enabled = true;
            roundaboutCam.tag = "MainCamera";
            sideTopCam.enabled = false;
            topCam.enabled = false;
            busCam.enabled = false;
            trafficLightCam.enabled = false;
            parkingLotCam.enabled = false;

        }
        else if (Input.GetKeyDown("4"))
        {
            // TRAFFIC LIGHT CAMERA
            trafficLightCam.enabled = true;
            trafficLightCam.tag = "MainCamera";
            sideTopCam.enabled = false;
            topCam.enabled = false;
            busCam.enabled = false;
            roundaboutCam.enabled = false;
            parkingLotCam.enabled = false;
        }
        else if (Input.GetKeyDown("5"))
        {
            // TOP CAMERA
            topCam.enabled = true;
            topCam.tag = "MainCamera";
            sideTopCam.enabled = false;
            busCam.enabled = false;
            trafficLightCam.enabled = false;
            roundaboutCam.enabled = false;
            parkingLotCam.enabled = false;
        }
        else if (Input.GetKeyDown("6"))
        {
            // TOP CAMERA
            parkingLotCam.tag = "MainCamera";
            parkingLotCam.enabled = true;
            topCam.enabled = false;
            busCam.enabled = false;
            sideTopCam.enabled = false;
            trafficLightCam.enabled = false;
            roundaboutCam.enabled = false;
        }
        else if (Input.GetKeyDown("escape"))
        {
            Application.Quit();
        }
    }

}
