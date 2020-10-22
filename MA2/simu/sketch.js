W = 194
H = 118
function setup() {
  createCanvas( W, H);
  angleMode(DEGREES)
}

function X(x){
    nx = x + W/2 - 10
    return nx
}

function Y(y){
    ny = y + H/2 - 10
    return ny
}

function draw() {
  background(150);
  fill(204);
  // translate(X(0), Y(0));
  // translate(80, -23)
  // rotate(57)
  // triangle(0, 0, 0, 20, 30, 10);
  fill(0, 0, 255);
  translate(X(0), Y(0));
  // translate(-30, -50)
  rotate(215)
  triangle(0, 0, 0, 20, 30, 10);
}
