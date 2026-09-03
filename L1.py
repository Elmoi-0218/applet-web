import pandas as pd
import webbrowser
import plotly.graph_objs as go
from flask import Flask, request, render_template, send_file, redirect

app = Flask(__name__)
data_loaded = False
data = None

########################## Funcion del boton Calculate ################################################################
@app.route('/calculate', methods=['POST'])
def calculate():
    print("Calculating...")  # Depuración para verificar si se está ejecutando calculate()
    try:
        if request.method == 'POST':
            # Realizar los cálculos en función de los datos del formulario
            calculation_results = perform_lightning_calculations(request.form)
            # Abrir el archivo Calculo_L1.txt y enviarlo como una descarga
            return send_file('Calculo_L1.txt', as_attachment=True)
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

# Define la ruta para el botón Clear
@app.route('/clear', methods=['POST'])
def clear_data():
    clear()
    return redirect('/')


########################## Funcion del boton View ################################################################
@app.route('/view')
def view_file():
    form_data = process_form_data(request.form)
    Horiz_Distance = form_data['Horiz_Distance']
    Height_at_Tower = form_data['Height_at_Tower']

    # Extracting only 7 points for red dots
    red_points_x = Horiz_Distance[:7]
    red_points_y = Height_at_Tower[:7]

    # Create trace for red points
    trace_red_points = go.Scatter(x=red_points_x, y=red_points_y, mode='markers', marker=dict(color='red'), name='Conductor Preview')

    # Configuring layout
    layout = go.Layout(
        title='Conductor Preview',
        xaxis=dict(title='Horiz. Distance (m)'),
        yaxis=dict(title='Height at Tower (m)'),
        hovermode='closest',
        titlefont=dict(color='blue')  # Cambia el color del título aquí
    )

    # Create figure
    fig = go.Figure(data=[trace_red_points], layout=layout)

    # Convert figure to HTML
    graph_html = fig.to_html(full_html=False)
    
    return graph_html


####################### Funciones de los botones ###############################
@app.route('/')
def index():
    data_loaded = False  # Define data_loaded here
    return render_template('L1.html', data_loaded=data_loaded)


@app.route('/submit', methods=['POST'])
def submit():
    button_clicked = request.form['submit_button']
    print("Button clicked:", button_clicked)  # Debugging para verificar el valor del botón
    if button_clicked == 'Calculate':
        return calculate()
    elif button_clicked == 'Clear':
        return redirect('/clear')
    elif button_clicked == 'View':
        return view_file()
    elif button_clicked == 'Help':
        return redirect('help')
    else:
        return "Unknown action."


############################## Funcion del boton demo ################################################
def fill_demo_form():
    form_data = {}

    try:
        with open('Informacion.txt', 'r') as file:
            lines = file.readlines()

        # Buscar la posición de la sección de líneas de fase
        phase_wire_section_start = lines.index(next(line.strip() for line in lines if line.strip().startswith('PHASE WIRE DESCRIPTION'))) + 1
        phase_wire_section_end = lines.index('pan length\n', phase_wire_section_start)

        # Procesar cada línea de la sección de líneas de fase
        for line in lines[phase_wire_section_start:phase_wire_section_end]:
            parts = line.strip().split()
            circuit_number = parts[0]
            Ph_to_Ph_Voltage = parts[1]
            Phase_Angle = parts[2]
            Horiz_Distance = parts[3]
            Height_at_Tower = parts[4]
            Sag = parts[5]
            Number = parts[6]
            Diameter = parts[7]
            Spacing = parts[8]
            Insulator_Length = parts[9]

            form_data[f'num4_{circuit_number}'] = Ph_to_Ph_Voltage
            form_data[f'num5_{circuit_number}'] = Phase_Angle
            form_data[f'num6_{circuit_number}'] = Horiz_Distance
            form_data[f'num7_{circuit_number}'] = Height_at_Tower
            form_data[f'num8_{circuit_number}'] = Sag
            form_data[f'num9_{circuit_number}'] = Number
            form_data[f'num10_{circuit_number}'] = Diameter
            form_data[f'num11_{circuit_number}'] = Spacing
            form_data[f'num12_{circuit_number}'] = Insulator_Length

    except Exception as e:
        return f"An error occurred: {str(e)}"

    return form_data

@app.route('/demo', methods=['GET', 'POST'])
def demo():
    return render_template('L1.html', data_loaded=True)



####################### Definir datos por defecto para el formulario ##################################
@app.route('/default')
def default_data():
    data = {
        'number_of_shield_wires': '',
        'span_length': '',
        'ground_flash_density': '',
        'tower_surge_impedance': '',
        'phase_conductors': [
            {
                'Ph-to-Ph Voltage (kV)': '',
                'Phase Angle (m)': '',
                'Horiz. Distance (m)': '',
                'Height at Tower (m)': '',
                'Sag (m)': '',
                'Number': '',
                'Diameter (cm)': '',
                'Spacing (cm)': '',
                'Insulator Length (m)': ''
            }
            for _ in range(6)
        ],
        'shield_wires': ['', '', '', ''],
        'low_frequency_footing_resistance': '',
        'account_for_earth_ionization': '',
        'korsuncev_s_dimension': '',
        'earth_resistivity': '',
        'earth_critical_ionization_gradient': ''
    }

    return render_template('L1.html', data=data, data_loaded=data_loaded)

@app.route('/process', methods=['POST'])
def process_file():
    if 'inputFile' not in request.files:
        return redirect(request.url)

    file = request.files['inputFile']
    if file.filename == '':
        return redirect(request.url)

    # Aquí va el procesamiento del archivo subido...

    message = "File processed successfully!"
    return render_template('L1.html', message=message)

@app.route('/submit_data', methods=['POST'])
def submit_data():
    # Aquí va el manejo de los datos enviados desde el formulario...
    form_data = request.form.to_dict()
    return render_template('L1.html', message="Data submitted successfully!")

################################## Funciones para los datos ###################################################################################    
def process_form_data(request_form):
    try:
        Ph_to_Ph_Voltage = [float(request_form.get(f'num4_{i}', 0.0)) for i in range(1, 7)]
        Phase_Angle = [float(request_form.get(f'num5_{i}', 0.0)) for i in range(1, 7)]
        Horiz_Distance = [float(request_form.get(f'num6_{i}', 0.0)) for i in range(1, 7)]
        Height_at_Tower = [float(request_form.get(f'num7_{i}', 0.0)) for i in range(1, 7)]
        Sag = [float(request_form.get(f'num8_{i}', 0.0)) for i in range(1, 7)]
        Number = [float(request_form.get(f'num9_{i}', 0.0)) for i in range(1, 7)]
        Diameter = [float(request_form.get(f'num10_{i}', 0.0)) for i in range(1, 7)]
        Spacing = [float(request_form.get(f'num11_{i}', 0.0)) for i in range(1, 7)]
        Insulator_Length = [float(request_form.get(f'num12_{i}', 0.0)) for i in range(1, 7)]
        Insulator_Orientation = request_form.get('Insulator_Orientation', '')
        Footing_Resistance = [float(request_form.get(f'num13_{i}', 0.0)) for i in range(1, 7)]
        Korsuncev_Dimension = float(request_form.get('num14', 0.0))
        Earth_Resistivity = float(request_form.get('num15', 0.0))
        Ionization_Gradient = float(request_form.get('num16', 0.0))

        return {
            'Ph_to_Ph_Voltage': Ph_to_Ph_Voltage,
            'Phase_Angle': Phase_Angle,
            'Horiz_Distance': Horiz_Distance,
            'Height_at_Tower': Height_at_Tower,
            'Sag': Sag,
            'Number': Number,
            'Diameter': Diameter,
            'Spacing': Spacing,
            'Insulator_Length': Insulator_Length,
            'Insulator_Orientation': Insulator_Orientation,
            'Footing_Resistance': Footing_Resistance,
            'Korsuncev_Dimension': Korsuncev_Dimension,
            'Earth_Resistivity': Earth_Resistivity,
            'Ionization_Gradient': Ionization_Gradient
        }
    except ValueError as e:
        return f"Error processing form data: {str(e)}"



def perform_lightning_calculations(request_form):
    # Obtener los datos del formulario
    form_data = process_form_data(request_form)

    # Realizar los cálculos
    flashes_to_phase_wires = sum(form_data['Number'])
    flashes_to_shield_wire = sum(form_data['Number']) * 2  # Ejemplo, ajustar según los datos reales
    total_flashes_to_line = flashes_to_phase_wires + flashes_to_shield_wire

    min_current_for_flashover = 6  # Ejemplo, ajustar según los datos reales
    min_current_for_backflashover = 95  # Ejemplo, ajustar según los datos reales

    flashovers_caused_by_shielding_failures = flashes_to_phase_wires
    backflashovers = sum(form_data['Number']) * 0.1  # Ejemplo, ajustar según los datos reales
    total_flashovers = flashovers_caused_by_shielding_failures + backflashovers

    breakdown_by_phase = {
        '1': {'Shielding Failures': form_data['Number'][0], 'Flashovers': form_data['Number'][0], 'Backflashovers': 1.3},
        '2': {'Shielding Failures': 0, 'Flashovers': 0, 'Backflashovers': 2.1},
        '3': {'Shielding Failures': 0, 'Flashovers': 0, 'Backflashovers': 2.0},
        '4': {'Shielding Failures': form_data['Number'][1], 'Flashovers': form_data['Number'][1], 'Backflashovers': 1.3},
        '5': {'Shielding Failures': 0, 'Flashovers': 0, 'Backflashovers': 2.1},
        '6': {'Shielding Failures': 0, 'Flashovers': 0, 'Backflashovers': 2.0}
    }

    total_breakdown = {
        'Shielding Failures': sum(form_data['Number']),
        'Flashovers': sum(form_data['Number']),
        'Backflashovers': sum([1.3, 2.1, 2.0])  # Ejemplo, ajustar según los datos reales
    }

    return {
        'flashes_to_phase_wires': flashes_to_phase_wires,
        'flashes_to_shield_wire': flashes_to_shield_wire,
        'total_flashes_to_line': total_flashes_to_line,
        'min_current_for_flashover': min_current_for_flashover,
        'min_current_for_backflashover': min_current_for_backflashover,
        'flashovers_caused_by_shielding_failures': flashovers_caused_by_shielding_failures,
        'backflashovers': backflashovers,
        'total_flashovers': total_flashovers,
        'breakdown_by_phase': breakdown_by_phase,
        'total_breakdown': total_breakdown
    }

################## Boton help ##################################################
@app.route('/help')
def help_page():
    return render_template('help.html')


if __name__ == '__main__':
    webbrowser.open('http://127.0.0.1:5000')
    app.run(debug=True,  use_reloader=False)
