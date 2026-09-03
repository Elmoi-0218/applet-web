import plotly.graph_objs as go
from flask import Flask, request, render_template, send_file, redirect

app = Flask(__name__)

@app.route('/submit_single_conductor', methods=['POST'])
def submit_single_conductor():
    id = request.form['id']
    diameter = request.form['diameter']
    voltage = request.form['voltage']
    angle = request.form['angle']
    height = request.form['height']
    coordinate = request.form['coordinate']
    
    # Realizar aquí cualquier operación necesaria con los datos recibidos
    
    return {
        'Id': id,
        'Diameter': diameter
    }

@app.route('/submit_regular_bundle', methods=['POST'])
def submit_regular_bundle():
    id = request.form['id']
    number = request.form['number']
    diameter = request.form['diameter']
    voltage = request.form['voltage']
    angle = request.form['angle']
    height = request.form['height']
    horizontal = request.form['horizontal']
    spacing = request.form['spacing']
    
    # Realizar aquí cualquier operación necesaria con los datos recibidos
    
    return "Regular bundle data received successfully!"

@app.route('/submit_irregular_bundle', methods=['POST'])
def submit_irregular_bundle():
    id = request.form['id']
    voltage = request.form['voltage']
    angle = request.form['angle']
    height = request.form['height']
    horizontal = request.form['horizontal']
    diameter = request.form.getlist('diameter[]')
    XR = request.form.getlist('XR[]')
    HR = request.form.getlist('HR[]')
    
    # Realizar aquí cualquier operación necesaria con los datos recibidos
    
    return "Irregular bundle data received successfully!"

# Renderizar la página HTML
@app.route('/')
def index():
    return render_template('AN1.html')

########################## Funcion del boton Calculate ################################################################
@app.route('/calculate', methods=['POST'])
def calculate():
    print("Calculating...")  # Depuración para verificar si se está ejecutando calculate()
    try:
        if request.method == 'POST':
            # Realizar los cálculos en función de los datos del formulario
            # Abrir el archivo Calculo_L1.txt y enviarlo como una descarga
            return send_file('Calculo_AN1.txt', as_attachment=True)
        else:
            return "Method not allowed for this route."
    except Exception as e:
        return f"An error occurred: {str(e)}", 500
    

########################## Funcion del boton Clear ################################################################ 
def clear():
    global data_loaded, data
    data_loaded = False
    data = None
    # Borra los datos de los campos del formulario
    for key in request.form:
        request.form[key] = ''

@app.route('/clear', methods=['POST'])
def clear_data():
    clear()
    return redirect('/')

########################## Funcion del boton View ################################################################
@app.route('/view', methods=['POST'])
def view_file():
    form_data = process_form_data(request.form)
    Horiz_Distance = form_data['Horizontal_Coordinate']
    Height_at_Tower = form_data['Height_above_Ground']

    # Extracting only 7 points for red dots
    red_points_x = Horiz_Distance[:7]
    red_points_y = Height_at_Tower[:7]

    # Create trace for red points
    trace_red_points = go.Scatter(x=red_points_x, y=red_points_y, mode='markers', marker=dict(color='red'), name='Conductor Preview')

    # Configuring layout
    layout = go.Layout(
        title='Conductor Preview',
        xaxis=dict(title='Horiz. Distance (m)'),
        yaxis=dict(title='Height above Ground(m)'),
        hovermode='closest',
        titlefont=dict(color='blue')  # Cambia el color del título aquí
    )

    # Create figure
    fig = go.Figure(data=[trace_red_points], layout=layout)

    # Convert figure to HTML
    graph_html = fig.to_html(full_html=False)
    
    return graph_html

################################## Funciones para los datos ###################################################################################    
def process_form_data(request_form):
    try:
        Bundle_ID = [request_form.get(f'num4_{i}', '') for i in range(1, 9)]
        Number_Subconductors = [float(request_form.get(f'num5_{i}', 0.0)) for i in range(1, 9)]
        Subconductors_Diameter = [float(request_form.get(f'num6_{i}', 0.0)) for i in range(1, 9)]
        Voltage_to_Ground = [float(request_form.get(f'num7_{i}', 0.0)) for i in range(1, 9)]
        Phase_Angle = [float(request_form.get(f'num8_{i}', 0.0)) for i in range(1, 9)]
        Horizontal_Coordinate = [float(request_form.get(f'num9_{i}', 0.0)) for i in range(1, 9)]
        Height_above_Ground = [float(request_form.get(f'num10_{i}', 0.0)) for i in range(1, 9)]

        return {
            'Bundle_ID': Bundle_ID,
            'Number_Subconductors': Number_Subconductors,
            'Subconductors_Diameter': Subconductors_Diameter,
            'Voltage_to_Ground': Voltage_to_Ground,
            'Phase_Angle': Phase_Angle,
            'Horizontal_Coordinate': Horizontal_Coordinate,
            'Height_above_Ground': Height_above_Ground
        }
    except ValueError as e:
        return f"Error processing form data: {str(e)}"
    
################## Boton help ################################################## 
@app.route('/help', methods=['GET'])
def help_page():
    return render_template('AN1-Help.html')

####################### Funciones de los botones ###############################
@app.route('/submit', methods=['POST'])
def submit():
    button_clicked = request.form['submit_button']
    print("Button clicked:", button_clicked)  # Debugging para verificar el valor del botón
    if button_clicked == 'Calculate':
        return calculate()
    elif button_clicked == 'Clear':
        return clear_data()
    elif button_clicked == 'View':
        return view_file()
    elif button_clicked == 'Help':
        return help_page('/help')
    else:
        return "Unknown action"

if __name__ == '__main__':
    app.run(debug=True)
