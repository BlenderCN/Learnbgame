function buttonAction(obj) {
  checkBox = $(obj).find("input[type=checkbox]").closest("input")[0];
  checkBox.checked = true;
  checkBox.disabled = true;
  obj.disabled = true;
  var commands = []
  for (var attr in obj.attributes) {
    if (obj.attributes[attr].name && obj.attributes[attr].name.startsWith("command")) {
      var command = obj.attributes[attr].value;
      commands.push(command)
    }
  }

  var commands_len = commands.length - 1
  for (var counter in commands) {
    var seq_command = commands[counter]+"&_seq="+counter+"/"+commands_len;
    sendCommand(seq_command);
  }
}

function getObjectValue(obj){
  var prefixed_prop_name = obj.attributes["prop_name"].value;
  var button = $(obj).closest("button");
  var pointer = prefixed_prop_name.indexOf("_", 1) + 1;
  var prop_name = prefixed_prop_name.substring(pointer);
  var obj_value = "(";


  button.find("input[type="+obj.type+"][prop_name$='"+prop_name+"']").each(function () {
    obj_value += this.value + ",";
  });
  obj_value = obj_value.substring(0, obj_value.length - 1);
  obj_value += ")";
  return [obj_value, prop_name]
}

function syncPropertyValue(obj){

  var button = $(obj).closest("button");
  var prop_name = obj.attributes["prop_name"].value;
  var node_name = button[0].attributes["node_name"].value;
  var value = null;

   button.find("[prop_name="+prop_name+"]").each(function(){
    this.value = obj.value;
  });

  if (prop_name.startsWith("_")){
    [value, prop_name] = getObjectValue(obj);
  } else {
    value = obj.value;
  }
  var command = "change_prop&node_name="+node_name+"&prop_name="+prop_name+"&value="+value;

  sendCommand(command);

}

function centerView(){
  var command = "view_all";
  sendCommand(command);
}

function resetView(){
  var command = "clear_node_groups";
  sendCommand(command);
  $(document).find("input[type=checkbox]").each(function(){
    this.checked = false;
    this.disabled = false;
  });
  $(document).find("button[type=button]").each(function(){
    this.disabled = false;
  });
}

function sendCommand(command){
  var BASE_URL = "http://localhost:4000/node/?command=";
  var url = BASE_URL + command;
  console.log(url);

  $.ajax({
       url: url,
       type: "GET",
       success: function(data) {console.log("OK");}
    });

}