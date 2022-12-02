using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class MakeCity : MonoBehaviour
{
    [SerializeField] TextAsset layout;
    [SerializeField] GameObject roadPrefab;
    [SerializeField] GameObject sidewalkPrefab;
    [SerializeField] int tileSize;

    // Start is called before the first frame update
    void Start()
    {
        MakeTiles(layout.text);
    }

    void MakeTiles(string tiles)
    {
        int x = 0;
        // Mesa has y 0 at the bottom
        // To draw from the top, find the rows of the file
        // and move down
        // Remove the last enter, and one more to start at 0
        int y = tiles.Split('\n').Length - 1;

        Vector3 position;
        GameObject tile;

        for (int i = 0; i < tiles.Length; i++)
        {
            if (tiles[i] == '>' || tiles[i] == '<')
            {
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(roadPrefab, position, Quaternion.identity);
                tile.transform.parent = transform;
                x += 1;
            }
            else if (tiles[i] == 'v' || tiles[i] == '^')
            {
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(roadPrefab, position, Quaternion.Euler(0, 90, 0));
                tile.transform.parent = transform;
                x += 1;
            }
            else if (tiles[i] == '=')
            {
                position = new Vector3(x * tileSize, 0.025f, y * tileSize);
                tile = Instantiate(sidewalkPrefab, position, Quaternion.identity);
                tile.transform.parent = transform;
                x += 1;
            }
            else if (tiles[i] == '\n')
            {
                x = 0;
                y -= 1;
            }
            else
            {
                x += 1;
            }
        }
    }
}
