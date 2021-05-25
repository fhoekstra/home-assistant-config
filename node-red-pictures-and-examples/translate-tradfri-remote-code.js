// I use this to translate codes of Tradfri remotes at the start of the "buttons"
//  Node-Red flow

// Only works properly for top and bottom buttons on tradfri remote
var press_types = {
    1: "hold",
    2: "short",
    3: "release"
}

var button_positions = {
    1000: "middle",
    2000: "top",
    3000: "bottom",
    4000: "left",
    5000: "right"
}

var new_payload = {}

new_payload.remote_name = msg.payload.event.id;

var button_code = msg.payload.event.event;

var button_thousands = button_code - button_code % 1000;
new_payload.button_position = button_positions[button_thousands];

var press_type_id = button_code % 1000;
new_payload.press_type = press_types[press_type_id];


return {"payload": new_payload};
