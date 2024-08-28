from apps import crete_app

app = crete_app()
#small change #0.0.6
import warnings


warnings.filterwarnings("ignore", message=".*CosmosDB cluster.*")

if __name__ == "__main__":
    app.run(debug=True,port=8000)

