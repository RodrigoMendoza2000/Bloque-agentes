from flask import Flask, request, jsonify
from model import *
from agent import *

# Size of the board:
NUMBER_OF_CARS = 5
randomModel = None
currentStep = 0

app = Flask("Traffic Base")


@app.route('/init', methods=['POST', 'GET'])
def initModel():
    global NUMBER_OF_CARS, randomModel

    # Datos que estamos mandando
    if request.method == 'POST':
        NUMBER_OF_CARS = int(request.form.get('N'))

        # Aquí se crea el modelo
        randomModel = RandomModel(NUMBER_OF_CARS)
        print(NUMBER_OF_CARS)

        return jsonify({"message": "Parameters recieved, model initiated."})


@app.route('/getAgents', methods=['GET'])
def getAgents():
    global randomModel

    if request.method == 'GET':
        # List comprehension
        agentsPositions = []
        for i in list(randomModel.grid.coord_iter()):
            agents = i[0]
            x = i[1]
            z = i[2]
            for a in agents:
                if isinstance(a, Car):
                    agentsPositions.append(
                        {"id": str(a.unique_id),
                         "x": x,
                         "y": 0,
                         "z": z})

        return jsonify({"positions": agentsPositions})


# Se encarga de hacerle el update al modelo, puede ser muy tardado
@app.route('/update', methods=['GET'])
def updateModel():
    global currentStep, randomModel
    if request.method == 'GET':
        randomModel.step()
        currentStep += 1
        return jsonify({'message': f'Model updated to step {currentStep}.',
                        'currentStep': currentStep})


if __name__ == '__main__':
    app.run(host="localhost", port=8585, debug=True)
