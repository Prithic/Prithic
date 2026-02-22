import json
import os
import sys
import random

BOARD_FILE = "space-game/board.json"
SVG_FILE = "space-game/space-game.svg"

WIDTH = 25
HEIGHT = 5

def load_game():
    with open(BOARD_FILE, "r") as f:
        return json.load(f)

def save_game(state):
    with open(BOARD_FILE, "w") as f:
        json.dump(state, f, indent=2)

def generate_svg(state):
    svg_header = '<svg xmlns="http://www.w3.org/2000/svg" width="600" height="250"><rect width="100%" height="100%" fill="#0D1117" rx="10"/>'
    svg_footer = '</svg>'
    svg_content = ""

    # Add grid/stars
    for _ in range(20):
        x = random.randint(0, 600)
        y = random.randint(0, 200)
        svg_content += f'<circle cx="{x}" cy="{y}" r="1" fill="#FFFFFF" opacity="0.3"/>'

    # Add text
    svg_content += f'<text x="20" y="30" fill="#3B82F6" font-family="Courier New" font-weight="bold" font-size="20">SCORE: {state["score"]}  HIGH SCORE: {state["high_score"]}</text>'

    if state["game_over"]:
        svg_content += f'<text x="300" y="125" fill="#EF4444" font-family="Courier New" font-weight="bold" font-size="30" text-anchor="middle">GAME OVER!</text>'
        svg_content += f'<text x="300" y="160" fill="gray" font-family="Courier New" font-size="15" text-anchor="middle">Click any action to restart.</text>'
    else:
        # Draw ship
        ship_x_pos = 50
        ship_y_pos = 50 + (state["ship_y"] * 40)
        svg_content += f'<text x="{ship_x_pos}" y="{ship_y_pos}" font-size="25">🚀</text>'

        # Draw lasers
        for laser in state["lasers"]:
            lx = 50 + (laser["x"] * 24)
            ly = 50 + (laser["y"] * 40) - 10
            svg_content += f'<rect x="{lx+25}" y="{ly}" width="15" height="4" fill="#10B981" rx="2"/>'

        # Draw asteroids
        for ast in state["asteroids"]:
            ax = 50 + (ast["x"] * 24)
            ay = 50 + (ast["y"] * 40)
            svg_content += f'<text x="{ax}" y="{ay}" font-size="25">☄️</text>'

    with open(SVG_FILE, "w", encoding="utf-8") as f:
        f.write(svg_header + svg_content + svg_footer)

def reset_game(state):
    return {
        "ship_y": 2,
        "asteroids": [{"x": 10, "y": 1}, {"x": 15, "y": 3}, {"x": 20, "y": 2}],
        "lasers": [],
        "score": 0,
        "high_score": state.get("high_score", 0),
        "game_over": False
    }

def process_turn(action):
    state = load_game()
    
    # Restart
    if state["game_over"]:
        state = reset_game(state)
        generate_svg(state)
        save_game(state)
        return

    # Process Input
    if action == "up" and state["ship_y"] > 0:
        state["ship_y"] -= 1
    elif action == "down" and state["ship_y"] < HEIGHT - 1:
        state["ship_y"] += 1
    elif action == "shoot":
        state["lasers"].append({"x": 1, "y": state["ship_y"]})

    # Move lasers and asteroids
    new_lasers = []
    for l in state["lasers"]:
        l["x"] += 2
        if l["x"] < WIDTH:
            new_lasers.append(l)
    state["lasers"] = new_lasers

    new_asteroids = []
    for a in state["asteroids"]:
        a["x"] -= 1
        # Collision checking (Laser hits Asteroid)
        destroyed = False
        for l in state["lasers"]:
            if l["y"] == a["y"] and abs(l["x"] - a["x"]) <= 1:
                destroyed = True
                state["score"] += 10
                state["lasers"].remove(l)
                break
        
        if not destroyed:
            # Collision checking (Asteroid hits Ship)
            if a["x"] <= 1 and a["y"] == state["ship_y"]:
                state["game_over"] = True
            
            if a["x"] >= 0:
                new_asteroids.append(a)
            else:
                state["score"] += 1

    # Spawn new asteroid
    if not state["game_over"] and random.random() < 0.6:
        new_asteroids.append({"x": WIDTH, "y": random.randint(0, HEIGHT - 1)})

    state["asteroids"] = new_asteroids

    # High score check
    if state["score"] > state["high_score"]:
        state["high_score"] = state["score"]

    save_game(state)
    generate_svg(state)

if __name__ == "__main__":
    action = "none"
    if len(sys.argv) > 1:
        action = sys.argv[1].lower()
    
    if action in ["up", "down", "shoot"]:
        process_turn(action)
    elif action == "init":
        # Just generate initial board
        generate_svg(load_game())
