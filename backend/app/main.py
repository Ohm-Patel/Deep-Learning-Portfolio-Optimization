from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.portfolio import router as portfolio_router

app = FastAPI(
    title="Portfolio Optimizer API",
    description="LSTM-based portfolio optimization with Monte Carlo simulations",
    version="1.0"
)

app.include_router(portfolio_router)

# CORS configuration (for React frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
@app.get("/")
def health_check():
    return {"status": "active"}

@app.get("/_diag/env")
def diag():
    import sys, json
    info = {
        "python_executable": sys.executable,
        "python_version": sys.version,
    }
    try:
        import keras
        info["keras_version"] = keras.__version__
        info["keras_path"] = getattr(keras, "__file__", None)
    except Exception:
        info["keras_version"] = None
        info["keras_path"] = None

    import tensorflow as tf, numpy, h5py
    info["tensorflow_version"] = tf.__version__
    info["tf_keras_path"] = getattr(tf.keras, "__file__", None)
    info["numpy_version"] = numpy.__version__
    info["h5py_version"] = h5py.__version__
    return info