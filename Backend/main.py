from typing import Union
from fastapi import Request
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import Backend.db_handler as db
import Backend.generic_helper as gh
app = FastAPI()

inprogress_order = {}

@app.post("/")
async def handle_request(request : Request):
    #retrieve JSON data from the request
    payload = await request.json()
    
    # extract the necessary information from the payload
    # based on the structure of the WebhookRequest from dialogflow

    intent = payload['queryResult']['intent']['displayName']
    parameters = payload['queryResult']['parameters']
    output_contexts = payload['queryResult']['outputContexts']

    session_id = gh.extract_session_id(output_contexts[0]['name'])

    intent_handler_dict = {
        "order.add - context: ongoing-order": add_to_order,
        'order.remove - context: ongoing-order': remove_the_order,
        'order.complete - context: ongoing-order': complete_order,
        "track.order - context: ongoing-order": track_order
    }
    
    return intent_handler_dict[intent](parameters,session_id)

def add_to_order(parameters,session_id ):
    food_items = parameters["food-item"]
    quantity = parameters["number"]

    if len(food_items) != len(quantity):
        fulfillment_text = "Sorry! I didn't understand. Can you please specify the food items and quantity clearly"
    else:
        
        new_food_dict = dict(zip(food_items,quantity))
        
        if session_id in inprogress_order:
            current_food_dict = inprogress_order[session_id]
            current_food_dict.update(new_food_dict)
            inprogress_order[session_id] = current_food_dict
        else :
            inprogress_order[session_id] = new_food_dict
        
        order_str = gh.get_str_from_food_dict(inprogress_order[session_id])
        fulfillment_text = f"so far you have: {order_str}. do you want anything else?"
        
    return JSONResponse(content = {
        "fulfillmentText" : fulfillment_text
    })

def complete_order(parameters,session_id):
    if session_id not in inprogress_order:
        fulfillment_text = "I'am having a trouble finding your order. Kindly place a new order"
    else:
        order = inprogress_order[session_id]
        order_id = save_to_db(order)
        
        if order_id == -1:
            fulfillment_text = "Sorry, I couldn't place your order due to a backend error."\
                                "Please place a new order again."
        else:
            order_total = db.get_total_order_price(order_id)
            fulfillment_text = f"Awesome. we have placed your order."\
                                f"Here is your order id: {order_id}"\
                                f"Your order total is {order_total} which you can pay at the time of delivery!"
        del inprogress_order[session_id]
        
    return JSONResponse(content = {
        "fulfillmentText" : fulfillment_text
    })
                                


def save_to_db(order : dict):
    next_order_id = db.get_next_order_id()
    
    for food_item,quantity in order.items():
        rcode = db.insert_order_item(
            food_item,
            quantity,
            next_order_id
        )
        if rcode == -1:
            return -1
    db.insert_order_tracking(next_order_id,"In Progress")
        
    return next_order_id

def remove_the_order(parameters : dict,session_id : str):
    if session_id not in inprogress_order:
        
        return JSONResponse(content = {
            "fulfilmentText": "I'm having trouble finding your order. Sorry! can you place a new order"
        })
        
    current_order = inprogress_order[session_id]
    food_items = parameters["food-item"]
    
    removed_items = []
    no_such_items = []
    
    for item in food_items:
        if item not in current_order:
            no_such_items.append(item)
        else:
            removed_items.append(item)
            del current_order[item]
            
    if len(removed_items) > 0:
        fulfillment_text = f'Removed {(",".join(removed_items))} from your order!'
    
    if len(no_such_items) > 0:
        fulfillment_text = f'Your current order does not have {",".join(no_such_items)}'
        
    if len(current_order.keys())==0:
        fulfillment_text +=" Your order is empty!"
    
    else:
        order_str = gh.get_str_from_food_dict(current_order)
        fulfillment_text +=f" Here is what left in yout order: {order_str}"
        
    return JSONResponse(content = {
        "fulfillmentText" : fulfillment_text
    })

def track_order(parameters : dict, session_id :str) : 
    order_id = int(parameters['number'])

    order_status = db.get_order_status(order_id)
    
    if order_status:
        fulfillment_text = f"the order status for {order_id} is : {order_status}"
    else:
        fulfillment_text = f"No order found for order_id : {order_id}"
        
    return JSONResponse(content = {
        "fulfillmentText" : fulfillment_text
    })