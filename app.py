from flask import Flask, render_template, jsonify
import corn_model

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_output/<output_type>')
def get_output(output_type):
    try:
        if output_type == 'summary':
            result = corn_model.generate_summary()
            return jsonify({"type": "text", "content": result})

        elif output_type == 'returns':
            corn_model.plot_returns()
            return jsonify({"type": "image", "url": "static/returns_plot.png"})

        elif output_type == 'regression':
            corn_model.plot_regression()
            return jsonify({"type": "image", "url": "static/regression_plot.png"})
        
        elif output_type == "regression_stats":
            with open("static/capm_summary.txt", "r", encoding="utf-8") as f:
                content = f.read()    
            return jsonify({"type": "text", "content": content})


        elif output_type == 'sml':
            corn_model.plot_sml()
            return jsonify({"type": "image", "url": "static/sml_graph.png"})

        else:
            return jsonify({"type": "text", "content": "Invalid output type."})
    except Exception as e:
        return jsonify({"type": "text", "content": f"Error: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)
