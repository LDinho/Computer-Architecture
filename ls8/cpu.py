"""CPU functionality."""

import sys

LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010

ADD = 0b10100000
PUSH = 0b01000101  # Push instruction on stack
POP = 0b01000110  # Pop instruction off stack

CALL = 0b01010000  # Jump to a subroutine's address
RET = 0b00010001  # Go to return address after subroutine is done

CMP = 0b10100111  # Compare - if values are equal set E flag to 1, else to zero
JMP = 0b01010100  # Jump to addr stored
JEQ = 0b01010101  # Jump to addr if equal flag is true
JNE = 0b01010110  # Jump to addr if equal flag is false

# flags:
# L = 0
# E = 0
# G = 0


is_running = True


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.sp = 7  # 8th register position
        self.flags = [0]*8

    def ram_read(self, address):
        data = self.ram[address]
        return data

    def ram_write(self, address, data):
        self.ram[address] = data

    def load(self, filename):
        """Load a program into memory."""

        # address = 0

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]
        #
        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1

        try:
            address = 0

            with open(filename) as file:  # open file

                for line in file:  # read each line
                    comment_split = line.split("#")  # remove comments
                    number_string = comment_split[0].strip()  # remove new lines

                    if number_string == "":  # ignore blank lines
                        continue
                    instruction_number = int(number_string, 2)

                    # this just prints out the binary code and conversion to decimal
                    # print(f'{instruction_number:08b} is {instruction_number:0d}')

                    self.ram[address] = instruction_number  # populate memory array
                    address += 1

        except FileNotFoundError:
            print("no file found")
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == ADD:
            self.reg[reg_a] += self.reg[reg_b]

        elif op == MUL:
            self.reg[reg_a] *= self.reg[reg_b]

        # elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""

        while is_running:  # while running is True

            opcode = self.ram[self.pc]
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            if opcode == LDI:
                self.reg[operand_a] = operand_b
                self.pc += 3
            elif opcode == PRN:
                print(self.reg[operand_a])
                self.pc += 2
            elif opcode == MUL:
                self.alu(opcode, operand_a, operand_b)
                self.pc += 3

            elif opcode == ADD:
                self.alu(opcode, operand_a, operand_b)
                self.pc += 3

            elif opcode == PUSH:
                # record value to be pushed on stack
                operand_a = self.ram_read(self.pc + 1)
                self.ram_write(self.sp, self.reg[operand_a])
                self.sp -= 1  # decrement stack pointer (memory by 1)
                self.pc += 2  # (since we have one argument)

            elif opcode == POP:
                operand_a = self.ram_read(self.pc + 1)
                self.reg[operand_a] = self.ram_read(self.sp + 1)
                self.sp += 1  # increment stack pointer
                self.pc += 2

            elif opcode == CALL:
                val = self.pc + 2
                reg = self.ram[self.pc + 1]
                subroutine_addr = self.reg[reg]

                self.reg[self.sp] -= 1  # decrement stack pointer
                self.ram[self.reg[self.sp]] = val

                self.pc = subroutine_addr  # update address

            elif opcode == RET:
                return_addr = self.reg[self.sp]
                self.pc = self.ram[return_addr]

                self.reg[self.sp] += 1

            elif opcode == CMP:
                self.flags = CMP

                if self.reg[self.ram_read(self.pc+1)] < self.reg[self.ram_read(self.pc+2)]:
                    L = 1
                    G = 0
                    E = 0
                    self.flags = 0b00000100

                elif self.reg[self.ram_read(self.pc+1)] > self.reg[self.ram_read(self.pc+2)]:
                    L = 0
                    G = 1
                    E = 0
                    self.flags = 0b00000010

                elif self.reg[self.ram_read(self.pc+1)] == self.reg[self.ram_read(self.pc+2)]:
                    L = 0
                    G = 0
                    E = 1
                    self.flags = 0b00000001

                self.pc += 3

            elif opcode == JMP:
                self.pc = self.reg[self.ram_read(self.pc+1)]

            elif opcode == JEQ:
                if E == 1:
                    self.pc = self.reg[self.ram_read(self.pc+1)]
                else:
                    self.pc += 2

            elif opcode == JNE:
                if E == 0:
                    self.pc = self.reg[self.ram_read(self.pc+1)]
                else:
                    self.pc += 2

            elif opcode == HLT:
                sys.exit(0)
            else:
                print(f"running program failed")
                sys.exit(2)
