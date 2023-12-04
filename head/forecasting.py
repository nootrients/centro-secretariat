from pmdarima import auto_arima
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error
from math import sqrt
import warnings

def forecast_scholarship_type(df, scholarship_type):
    train_size = int(len(df) * 0.8)
    train, test = df[:train_size], df[train_size:]

    best_mse_new = float('inf')
    best_order_new = None
    best_mse_renewing = float('inf')
    best_order_renewing = None

    # Grid search for ARIMA parameters for new applicants
    for p in range(6):
        for d in range(4):
            for q in range(4):
                order = (p, d, q)
                try:
                    with warnings.catch_warnings():
                        warnings.filterwarnings("ignore")
                        model = ARIMA(train[f'{scholarship_type}_New'], order=order)
                        model_fit = model.fit()
                        predictions_new = model_fit.forecast(steps=len(test))
                        mse_new = mean_squared_error(test[f'{scholarship_type}_New'], predictions_new)
                        print(f'Order (New): {order}, MSE: {mse_new}')

                        if mse_new < best_mse_new:
                            best_mse_new = mse_new
                            best_order_new = order

                except Exception as e:
                    print(f"Error for order {order}: {e}")
                    continue

    print(f'Best Order (New): {best_order_new}, Best MSE: {best_mse_new}')

    # Grid search for ARIMA parameters for renewing applicants
    for p in range(6):
        for d in range(4):
            for q in range(4):
                if p + d + q > 0:  # Avoid ARIMA(0,0,0)
                    order = (p, d, q)

                    # Suppress ARIMA warnings
                    try:
                        with warnings.catch_warnings():
                            warnings.filterwarnings("ignore")
                            model = ARIMA(train[f'{scholarship_type}_Renewing'], order=order)
                            model_fit = model.fit()
                            predictions_renewing = model_fit.forecast(steps=len(test))
                            mse_renewing = mean_squared_error(test[f'{scholarship_type}_Renewing'], predictions_renewing)

                            print(f'Order (Renewing): {order}, MSE: {mse_renewing}')

                            if mse_renewing < best_mse_renewing:
                                best_mse_renewing = mse_renewing
                                best_order_renewing = order

                    except Exception as e:
                        print(f"Error for order {order}: {e}")
                        continue

    print(f'Best Order (Renewing): {best_order_renewing}, Best MSE: {best_mse_renewing}')

    return best_order_new, best_order_renewing, test