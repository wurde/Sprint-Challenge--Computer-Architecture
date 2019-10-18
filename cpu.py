"""CPU functionality."""

#
# Dependencies
#

import sys

#
# Constants
#

# Stack pointer is register R7
SP = 7
# Interrupt status is register R6
IS = 6
# Interrupt mask is register R5
IM = 5
# Opcodes
NOP  = 0b00000000
HLT  = 0b00000001
RET  = 0b00010001
CALL = 0b01010000
JMP  = 0b01010100
JEQ  = 0b01010101
JNE  = 0b01010110
PUSH = 0b01000101
POP  = 0b01000110
PRA  = 0b01001000
PRN  = 0b01000111
LDI  = 0b10000010
LD   = 0b10000011
ST   = 0b10000100
INC  = 0b01100101
DEC  = 0b01100110
ADD  = 0b10100000
SUB  = 0b10100001
AND  = 0b10101000
OR   = 0b10101010
XOR  = 0b10101011
NOT  = 0b01101001
SHL  = 0b10101100
SHR  = 0b10101101
CMP  = 0b10100111
MUL  = 0b10100010

#
# Class definition
#

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.running = False

        # 256 bytes of memory
        self.ram = [0] * 256
        # Create 8 registers, 1 byte each
        self.reg = [0] * 8

        self.ir = 0   # Instruction Register
        self.pc = 0   # Program Counter
        self.mar = 0  # Memory Address Register
        self.mdr = 0  # Memory Data Register
        self.fl = 0   # Flags
        self.reg[IM] = 0
        self.reg[IS] = 0
        self.reg[SP] = 0xF4

        self.branchtable = {}
        self.branchtable[NOP]  = self.handle_nop
        self.branchtable[HLT]  = self.handle_hlt
        self.branchtable[RET]  = self.handle_ret
        self.branchtable[CALL] = self.handle_call
        self.branchtable[JMP]  = self.handle_jmp
        self.branchtable[JEQ]  = self.handle_jeq
        self.branchtable[JNE]  = self.handle_jne
        self.branchtable[PUSH] = self.handle_push
        self.branchtable[POP]  = self.handle_pop
        self.branchtable[PRA]  = self.handle_pra
        self.branchtable[PRN]  = self.handle_prn
        self.branchtable[LDI]  = self.handle_ldi
        self.branchtable[LD]   = self.handle_ld
        self.branchtable[ST]   = self.handle_st
        self.branchtable[INC]  = self.handle_inc
        self.branchtable[DEC]  = self.handle_dec
        self.branchtable[ADD]  = self.handle_add
        self.branchtable[SUB]  = self.handle_sub
        self.branchtable[AND]  = self.handle_and
        self.branchtable[OR]   = self.handle_or
        self.branchtable[XOR]  = self.handle_xor
        self.branchtable[NOT]  = self.handle_not
        self.branchtable[SHL]  = self.handle_shl
        self.branchtable[SHR]  = self.handle_shr
        self.branchtable[MUL]  = self.handle_mul
        self.branchtable[CMP]  = self.handle_cmp

    def load(self, filename):
        """Load a program into memory."""

        try:
            address = 0

            f = open(filename, 'r')
            lines = f.readlines()
            f.close()

            for line in lines:
                # Process comments: Ignore anything after a # symbol
                comment_split = line.split("#")

                # Convert any numbers from binary strings to integers
                num = comment_split[0].strip()
                try:
                    val = int(num, 2)
                except ValueError:
                    continue

                self.ram[address] = val
                address += 1

        except FileNotFoundError:
            print(f"{sys.argv[0]}: {sys.argv[1]} not found")
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == ADD:
            self.reg[reg_a] += self.reg[reg_b]
        elif op == SUB:
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == MUL:
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == INC:
            self.reg[reg_a] += 1
        elif op == DEC:
            self.reg[reg_a] -= 1
        elif op == AND:
            self.reg[reg_a] = self.reg[reg_b] & self.reg[reg_b]
        elif op == OR:
            self.reg[reg_a] = self.reg[reg_b] | self.reg[reg_b]
        elif op == XOR:
            self.reg[reg_a] = self.reg[reg_b] ^ self.reg[reg_b]
        elif op == NOT:
            self.reg[reg_a] = 0b11111111 - self.reg[reg_a]
        elif op == SHL:
            self.reg[reg_a] = self.reg[reg_a] << self.reg[reg_b]
        elif op == SHR:
            self.reg[reg_a] = self.reg[reg_a] >> self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        self.running = True

        while self.running:
            self.ir = self.ram_read(self.pc)

            if self.ir in self.branchtable:
                self.branchtable[self.ir]()
            else:
                print(f"Unknown instruction: {self.ir}")
                sys.exit(1)

            if self.pc >= len(self.ram) - 1:
                self.pc = 0
            else:
                self.pc += 1

    def ram_read(self, pc):
        return self.ram[pc]

    def ram_write(self, pc, instruction):
        self.ram[pc] = instruction

    def handle_nop(self):
        next

    def handle_hlt(self):
        self.running = False

    def handle_ret(self):
        register = self.ram_read(self.reg[SP])
        self.reg[SP] += 1
        self.pc = register - 1

    def handle_call(self):
        reg_a = self.reg[self.ram_read(self.pc + 1)]
        self.reg[SP] -= 1
        self.ram_write(self.reg[SP], self.pc + 2)
        self.pc = reg_a

    def handle_jmp(self):
        reg_a = self.reg[self.ram_read(self.pc + 1)]
        self.pc = reg_a - 1

    def handle_jeq(self):
        reg_a = self.reg[self.ram_read(self.pc + 1)]
        if self.fl == 1:
            # If equal flag is true, jump to the address stored in register.
            self.pc = reg_a - 1
        else:
            self.pc += 1

    def handle_jne(self):
        reg_a = self.reg[self.ram_read(self.pc + 1)]
        if self.fl > 1:
            # If equal flag is false, jump to the address stored in register.
            self.pc = reg_a - 1
        else:
            self.pc += 1

    def handle_push(self):
        register = self.ram_read(self.pc + 1)
        val = self.reg[register]
        self.reg[SP] -= 1
        self.ram_write(self.reg[SP], val)
        self.pc += 1

    def handle_pop(self):
        register = self.ram_read(self.pc + 1)
        val = self.ram_read(self.reg[SP])
        self.reg[register] = val
        self.reg[SP] += 1
        self.pc += 1

    def handle_pra(self):
        reg_a = self.ram_read(self.pc + 1)
        print(chr(self.reg[reg_a]))
        self.pc += 1

    def handle_prn(self):
        reg_a = self.ram_read(self.pc + 1)
        print(self.reg[reg_a])
        self.pc += 1

    def handle_ldi(self):
        reg_a = self.ram_read(self.pc + 1)
        val = self.ram_read(self.pc + 2)
        self.reg[reg_a] = val
        self.pc += 2

    def handle_ld(self):
        reg_a = self.ram_read(self.pc + 1)
        val = self.ram_read(self.pc + 2)
        self.reg[reg_a] = val
        self.pc += 2

    def handle_st(self):
        reg_a = self.ram_read(self.pc + 1)
        val = self.reg[self.ram_read(self.pc + 2)]
        self.reg[reg_a] = val
        self.pc += 2

    def handle_inc(self):
        reg_a = self.ram_read(self.pc + 1)
        self.alu(INC, reg_a, None)
        self.pc += 1

    def handle_dec(self):
        reg_a = self.ram_read(self.pc + 1)
        self.alu(DEC, reg_a, None)
        self.pc += 1

    def handle_add(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu(ADD, reg_a, reg_b)
        self.pc += 2

    def handle_sub(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu(SUB, reg_a, reg_b)
        self.pc += 2

    def handle_and(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu(AND, reg_a, reg_b)
        self.pc += 2

    def handle_or(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu(OR, reg_a, reg_b)
        self.pc += 2

    def handle_xor(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu(XOR, reg_a, reg_b)
        self.pc += 2

    def handle_not(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu(NOT, reg_a, reg_b)
        self.pc += 2

    def handle_shl(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu(SHL, reg_a, reg_b)
        self.pc += 2

    def handle_shr(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu(SHR, reg_a, reg_b)
        self.pc += 2

    def handle_mul(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu(MUL, reg_a, reg_b)
        self.pc += 2

    def handle_cmp(self):
        reg_a = self.reg[self.ram_read(self.pc + 1)]
        reg_b = self.reg[self.ram_read(self.pc + 2)]
        if reg_a == reg_b:
            # If equal, set the Equal `E` flag to 1, otherwise 0.
            self.fl = 0b00000001
        elif reg_a > reg_b:
            # If A greater than B, set Greater-than `G` flag to 1, otherwise 0.
            self.fl = 0b00000010
        elif reg_a < reg_b:
            # If A less than B, set Less-than `L` flag to 1, otherwise 0.
            self.fl = 0b00000100
        self.pc += 2
