# Probabilities for key changes from : to
WEIGHTS = {
    'd' : {
        'g' : .3,
        'em' : .3,
        'am' : .3,
        'a' : .1,
    },

    'g' : {
        'bm' : .15,
        'em' : .27,
        'am' : .35,
        'a' : .12,
		'd' : .35,
    },

    'em' : {
        'd' : .50,
        'g' : .40,
        'am' : .05,
        'bm' : .05,
    },

    'bm' : {
        'd' : .45,
        'g' : .45,
        'am' : .05,
        'em'  : .05,
    },

    'am' : {
        'd' : .47,
        'g' : .46,
        'a' : .07,
    },
}
