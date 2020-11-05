
let size = 4

let W = 194 * size
let H = 118 * size
let rW = 8 * size
let rH =  4 * size

function setup() {
  createCanvas( W , H );
  angleMode(DEGREES)
}

function X(x){
    return x * size + W / 2 - 5
}

function Y(y){
    return -1*y * size + H / 2  - 5
}

function robot(x, y, angle){
  push()
  translate(x*size, -1 * y * size )
  rotate(-1 * angle)
  // translate(X(x), Y(y))
  triangle(-rW / 4, -rH / 2, -rW / 4, +rH / 2, rW, 0);
  // triangle(x, y, x, y+5, x+10, y+2.5);
  pop()
  // triangle(nx, ny, nx, ny+5, nx+10, ny+2.5);
}

function draw() {
  background(150);
  fill(204);
  translate(W/2, H/2);
  robot(80, 30, 90)
  robot(80, -39, 45)
  robot(-80, 38, 226)
}
