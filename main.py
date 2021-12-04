import json

results = {}

def calculate_value(worker, order, tax, worker_value, total_orders):
    total_value = worker.get('total_value', 0) + ( order['price'] * tax) + worker_value
    worker.update({"total_value" : total_value, "total_orders" : total_orders})

def calculate_total_orders(worker):
    total = 1
    for item in worker['orders']:
        total = total + len(item['orders'])
    return total

def register_order(worker, store, order, results):
    store_name = store['name']
    store_tax = store['tax']

    if worker['name'] in results:
        worker_value = worker['value']
        worker =  results[worker['name']]
        total_orders = calculate_total_orders(worker)
        worker_orders = worker['orders']
        calculate_value(worker, order, store_tax, worker_value, total_orders)

        result = list(filter(lambda item: item['name'] == store_name, worker_orders))
        if len(result) > 0:
            result[0]['orders'].append(order['name'])
        else:
            data = {
                "name" : store_name,
                "orders" : [order['name']]
            }
            worker_orders.append(data)
        return True
    data = {
        "orders" : [
            {
                "name" : store_name,
                "orders" : [order['name']]
            }
        ],
        "total_value" : (order['price'] * store_tax) + worker['value'],
        "total_orders" : 1
    }
    results.update({worker['name'] : data})
    return True


def check_range_of_workers(workers_size, actual_worker_position):
    if actual_worker_position >= workers_size:
        return 0
    return actual_worker_position + 1

    
def check_priorities(store, workers):
    for idx, worker in enumerate(workers):
        if len(worker['places']) <= 1 and store in worker['places']:
            if not worker['name'] in results:
                return True, worker, idx 
    return False, None, None

def check_worker_availability(store, workers, actual_worker_position, workers_size):
    actual_worker_position = check_range_of_workers(workers_size, actual_worker_position)
    while(True):
        if store['name'] in workers[actual_worker_position]['places']:
            break
        else:
            actual_worker_position = check_range_of_workers(workers_size, actual_worker_position)
    return actual_worker_position
            

def main():
    with open('data.json') as json_file:
        data = json.load(json_file)
        workers = data['worker']
        stores = data['store']

        actual_worker_position = 0
        workers_size = len(workers) - 1

        for store in stores:
            for order in store['order']:
                #Check if there is any motoboy with priority and no order
                status, worker, priority_position = check_priorities(store['name'], workers)
                if priority_position:
                    actual_worker_position = priority_position
                if status:
                    register_order(worker, store, order, results)
                    actual_worker_position += 1
                    continue
                #Check and get the motoboy available
                if store['name'] in workers[actual_worker_position]['places']:
                    register_order(workers[actual_worker_position], store, order, results)
                else:
                    actual_worker_position = check_worker_availability(store, workers, actual_worker_position, workers_size)
                    register_order(workers[actual_worker_position], store, order, results)
                actual_worker_position = check_range_of_workers(workers_size, actual_worker_position)
    return results
                
if __name__ == "__main__":
    result = main()
    input = input("Select a courier or return all: ")
    try:
        print(result[input])
    except:
        print(result)