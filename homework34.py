import time
import threading
from threading import Thread, Lock
from queue import Queue

lock = Lock()

class Table:

    def __init__(self, number):
        self.number = number
        self.customer = None
        self.is_busy = False

    def start_serve(self, customer):
        with lock:
            self.is_busy = True
            self.customer = customer
            self.customer.start()
            print(f'Посетитель номер {self.customer.number} сел за стол {self.number}. (начало обслуживания)')

    def stop_serve(self):
        with lock:
            if self.customer != None:
                if self.customer.is_alive():
                    return False
                else:
                    print(f'Посетитель номер {self.customer.number} покушал и ушёл. (конец обслуживания)')
                    self.is_busy = False
                    return True
            else:
                return True

class Cafe:
    def __init__(self, tables):
        self.tables = tables
        self.queue = Queue()
        self.gost = 0
        self.open = True

    def customer_arrival(self, max_customs=10):
        for i in range(max_customs):
            self.gost += 1
            customer = Customer(self.gost)
            print(f'Посетитель номер {self.gost} прибыл')
            ind = None
            for i in range(len(self.tables)):
                if not self.tables[i].is_busy:
                    ind = i
                    break
            if ind is None:
                self.queue.put(customer)
                print(f'Посетитель {customer.number} ожидает свободный стол')
            else:
                self.tables[ind].start_serve(customer)
            time.sleep(1)
        self.open = False

    def serve_customer(self):
        tables_in_operation = False
        while self.open or tables_in_operation:
            tables_in_operation = False
            for table in self.tables:
                if table.stop_serve():
                    if self.queue.empty():
                        #print(f'Очередь пуста')
                        table.customer = None
                    else:
                        customer = self.queue.get()
                        table.start_serve(customer)
                else:
                    tables_in_operation = True
            time.sleep(0.2)
        print('Все посетители обслужены!')


class Customer(Thread):
    def __init__(self, number):
        super().__init__()
        self.number = number

    def run(self):
        time.sleep(5)



table1 = Table(1)
table2 = Table(2)
table3 = Table(3)
tables = [table1, table2, table3]

cafe = Cafe(tables)

customer_arrival_thread = Thread(target=cafe.customer_arrival, args=(20,))
customer_arrival_thread.start()
serve_customer_thread = Thread(target=cafe.serve_customer)
serve_customer_thread.start()
customer_arrival_thread.join()
serve_customer_thread.join()