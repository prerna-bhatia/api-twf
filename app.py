from flask import Flask, request, jsonify
from itertools import permutations

app = Flask(__name__)

product_data = {
    "A": {"center": "C1", "weight": 3},
    "B": {"center": "C1", "weight": 2},
    "C": {"center": "C1", "weight": 8},
    "D": {"center": "C2", "weight": 12},
    "E": {"center": "C2", "weight": 25},
    "F": {"center": "C2", "weight": 15},
    "G": {"center": "C3", "weight": 0.5},
    "H": {"center": "C3", "weight": 1},
    "I": {"center": "C3", "weight": 2}
}

distances = {
    ("C1", "C2"): 4, ("C2", "C1"): 4,
    ("C1", "C3"): 5, ("C3", "C1"): 5,
    ("C2", "C3"): 3, ("C3", "C2"): 3,
    ("C1", "L1"): 3, ("L1", "C1"): 3,
    ("C2", "L1"): 2.5, ("L1", "C2"): 2.5,
    ("C3", "L1"): 2, ("L1", "C3"): 2
}

def calculate_segment_cost(weight, distance):
    base_rate = 10
    
    if weight <= 5:
        return base_rate * distance
    elif weight <= 10:
        return (base_rate + 8) * distance
    elif weight <= 15:
        return (base_rate + 16) * distance
    else:
        additional_tiers = (weight - 5 + 4.999) // 5
        return (base_rate + (additional_tiers * 8)) * distance

def simulate_delivery(order):
    centers_to_visit = set()
    for product, qty in order.items():
        if qty > 0:
            centers_to_visit.add(product_data[product]["center"])
    
    if not centers_to_visit:
        return 0
    
    if len(centers_to_visit) == 1:
        center = list(centers_to_visit)[0]
        total_weight = sum(product_data[p]["weight"] * qty 
                      for p, qty in order.items() 
                      if qty > 0 and product_data[p]["center"] == center)
        
        return calculate_segment_cost(total_weight, distances[(center, "L1")])
    
    min_cost = float('inf')
    
    for perm in permutations(centers_to_visit):
        N = len(perm)
        for mask in range(2**(N-1)):
            cost = 0
            current_location = perm[0]
            current_weight = 0
            
            for product, qty in order.items():
                if qty > 0 and product_data[product]["center"] == current_location:
                    current_weight += product_data[product]["weight"] * qty
            
            for i in range(1, N):
                next_center = perm[i]
                
                deliver_first = (mask & (1 << (i-1))) != 0
                
                if deliver_first and current_weight > 0:
                    cost += calculate_segment_cost(current_weight, distances[(current_location, "L1")])
                    current_location = "L1"
                    current_weight = 0
                
                cost += calculate_segment_cost(current_weight, distances[(current_location, next_center)])
                current_location = next_center
                
                for product, qty in order.items():
                    if qty > 0 and product_data[product]["center"] == current_location:
                        current_weight += product_data[product]["weight"] * qty
            
            if current_weight > 0:
                cost += calculate_segment_cost(current_weight, distances[(current_location, "L1")])
            
            if cost < min_cost:
                min_cost = cost
    
    return int(min_cost)

@app.route('/calculate-cost', methods=['POST'])
def calculate_cost():
    data = request.get_json()
    min_cost = simulate_delivery(data)
    
    return jsonify({
        "message": "Delivery cost calculated successfully",
        "minimum_cost": min_cost
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)