# Imports
import logging
import azure.functions as func
from logic.main import main as main_function_logic

# Initialize Function App
app = func.FunctionApp()

# Schedule App Main Logic
@app.schedule(
    schedule="0 0 * * * *", # Activates Every Hour
    arg_name="myTimer",
    run_on_startup=True,
    use_monitor=False
)
def timer_trigger(myTimer: func.TimerRequest) -> None:
    
    # if past due, send warning message before run
    if myTimer.past_due:
        logging.info('The timer is past due!')

    # Main Logic
    main_function_logic()
    logging.info('Python timer trigger function executed.')