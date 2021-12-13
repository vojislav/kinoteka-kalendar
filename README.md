# kinoteka_kalendar
parser for the Yugoslav film archive monthy program, data from danubeogradu.rs

still in it's demo phase. the current plan is to make a Flask webpage to show the screenings and host it on my website.

it currently takes a link (for example, https://www.danubeogradu.rs/2021/04/kinoteka-repertoari-za-maj-2021/) as a command line argument
and prints a table of the film screenings.

i have tested it for all the screenings from this year including may (the ones from before then are in a different format).

the reason i didn't directly scrape from the YFA PDF they post every month is because the format was too difficult for me to work with and isn't consistent.

the format on danubeogradu.rs, while still not perfectly consistent, was consistent enough for me to succesfully scrape the screenings from this year.
i can only hope the format doesn't change further. maybe i'll get in contact with the guy who writes the programs and ask him to keep a regular format.

i was also thinking of contacting the YFA directly and asking them for a more parseable file, but that doesn't seem likely to get a response.
