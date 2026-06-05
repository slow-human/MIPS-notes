    .data
msg1:.asciiz"hello world!"
    .text
main:
    li $v0,4
    la $a0,msg1
    syscall
exit:
    li $v0,10
    syscall