********** VERSION 1 **********

function sleep(ms) {return new Promise(resolve => setTimeout(resolve, ms));}

let first_pause, second_pause, coordinate_Y, scrolldown_step
first_pause = 5000; // Pause to load first page
second_pause = 2000;  // Pause to load next pages
coordinate_Y = 0;  // Changes after every scrolldown
scrolldown_step = 600;

down();

function down(){
  coordinate_Y += scrolldown_step;
  sleep(second_pause)
  .then(() => console.log(`Scrolling (pause=${second_pause/1000} sec)...`))
  .then(() => window.scrollTo(0, coordinate_Y))
  .then((function check(){
    let scrollHeight, totalHeight;
    scrollHeight = document.body.scrollHeight;
    totalHeight = window.scrollY + window.innerHeight;
    if(totalHeight >= scrollHeight)
    {
        console.log("at the bottom");
    } else {
      down()
    }
        }));
};


********** VERSION 2 **********

<script>
let scroll_height = 0;
let i = 0;
function down() {
  window.scrollTo({ left: 0, top: scroll_height, behavior: "smooth"});
  let step = window.innerHeight;
  i++;
  console.log(`Scrolldown ${i}...`);
  console.log(`Window height (scrolldown step): ${step}`);
  scroll_height += step;
  let scrollHeight, totalHeight;
  scrollHeight = document.body.scrollHeight;
  totalHeight = window.scrollY + window.innerHeight;
  if (totalHeight >= scrollHeight) {
    console.log("at the bottom");
    clearInterval(timerID);
  }
}

let timerID = setInterval(down, 3000);
</script>


********** VERSION 3 **********

(function down() {
  let step = window.innerHeight;
  window.scrollTo(0, window.pageYOffset+step);
  console.log(`Window position: ${window.pageYOffset}`);
  let scrollHeight, totalHeight;
  scrollHeight = document.body.scrollHeight;
  totalHeight = window.scrollY + window.innerHeight;
  if (totalHeight >= scrollHeight) {
    console.log("at the bottom");
    return;
  } else { down() }
})()


********** VERSION 4 **********

[Move down from 0 (step=200) and then move up from the bottom (step=200)]

(function down() {
  let y=1;
  while ((window.scrollY + window.innerHeight) < document.body.scrollHeight){
    window.scrollTo(0, y*200);
    y++;
  };
  y=0;
  window.scrollTo(0, document.body.scrollHeight);
  while ((window.scrollY) > 0){
    window.scrollTo(0, document.body.scrollHeight - y*200);
    y++;
  };
  return 55;
})()