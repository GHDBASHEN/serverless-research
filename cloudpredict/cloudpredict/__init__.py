# Ensure lightgbm is imported before any other ML libraries or models are unpickled.
# On Windows, loading XGBoost before LightGBM causes an OpenMP runtime collision (access violation 0x00000000).
try:
    import lightgbm
except ImportError:
    pass
