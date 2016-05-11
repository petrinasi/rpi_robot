fs = require('fs');
http = require('http');
url = require('url');

var port = 8081;

http.createServer(function(req, res){
  var request = url.parse(req.url, true);
  var action = request.pathname;
  
  if (action == '/take_picture') {
    console.log("createServer: Taking picture");  
    takePicture(action.slice(1)+".py", res);
    console.log("createServer: Picture taken");
    res.writeHead(200, {'Content-Type': 'text/plain' });     
    res.end('Picture taken.\n');
  }
  else if (action == '/read_picture') {
    console.log("createServer: Reading picture");            
    var img = fs.readFileSync('./foo.jpg');
    res.writeHead(200, {'Content-Type': 'image/jpeg' });
    res.end(img, 'binary');
  } else { 
     res.writeHead(200, {'Content-Type': 'text/plain' });
     res.end('Hello World \n');
  }
}).listen(port);
console.log("Server started. Listening port "+port);

function takePicture(script, res) {
    var exec = require('child_process').exec,
        child;        
    child = exec('python '+script, function (error, stdout, stderr) {
        if (error !== null) {
            console.log('exec error: ' + error);
            
        }        
        else { 
            console.log("takePicture: picture taken");                        
        }  
    })    
}

