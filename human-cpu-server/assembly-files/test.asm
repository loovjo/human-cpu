; Sum all cubes from 0 to 10 using actors

; Actors:
;   Initer:
;       _start: create a Counter, count_down(10, 0, self-addr()) to it
;       done(val): print the value
;   Counter:
;       count_down(i, acc, response-addr):
;           if i == 0
;               sends done(acc) to response-addr
;           else:
;               sends count_down(i - 10, acc + i * i, response-addr) to self

#define created_counter 0
#define done 1
#define count-down 10

_start:
    make-handler
        created_counter
        1
        _on_created_counter

    create-actor
        counter_init
        1
        rhen

    idle

_on_created_counter:
    make-handler
        done
        1
        on_done

    Set [5] 10
    Set [6] 0
    self-addr [7]

    send-msg
        rhen
        count-down
        3
        5

    idle

on_done:
    idle

counter_init:


    send-msg
        rhen
        created_counter
        0
        0
