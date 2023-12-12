var mx = window.innerWidth - 16;
var my = window.innerHeight;
var num_flakes = 75;
if (mx < 800) num_flakes = 10
var flake_speed = 10;
var snow_rate = 250;
var flakes = new Array();
function flake()
{
    this.x = Math.random() * mx;
    this.y = -Math.random() * my;
    this.yd = flake_speed / 2 + Math.random() * flake_speed;
}
function snow()
{
    for( var i = 0; i < num_flakes; i++ )
    {
        if( typeof flakes[i] === 'undefined' || flakes[i].y >= my - flake_speed * 3 )
            flakes[i] = new flake();
        flakes[i].y += flakes[i].yd;
        var f = document.getElementById( 'f' + i );
        f.style.left = ~~flakes[i].x + 'px';
        f.style.top = ~~flakes[i].y + 'px';
    }
}
window.onload = function()
{
    for( var i = 0; i < num_flakes; i++ )
    {
        var e = document.createElement( 'span' )
        e.setAttribute( 'id', 'f' + i );
        e.setAttribute( 'class', 'flake' );
        document.body.appendChild( e );
    }
    setInterval( snow, snow_rate );
}
