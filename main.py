import sys
import math
import string
from functools import reduce

# Bring data on patient samples from the diagnosis machine to the laboratory with enough molecules to produce medicine!
ME = 0
ENEMY = 1
NO_DATA = -1
MOLECULES_LIST = list(string.ascii_uppercase[:5])
MOLECULES_DICT = dict(zip(MOLECULES_LIST, [0] * 5))
MAX_SAMPLES = 3
MAX_MOLECULES = 10
BAD_SAMPLE = 10


class go:
    def samples():
        add_command('GOTO  SAMPLES')

    def diagnosis():
        add_command('GOTO  DIAGNOSIS')

    def molecules():
        add_command('GOTO MOLECULES')

    def lab():
        add_command('GOTO LABORATORY')


class do:
    def diagnose(id):
        add_command(f'CONNECT {id}')

    def upload(id):
        add_command(f'CONNECT {id}')

    def download(id):
        add_command(f'CONNECT {id}')

    def collect_molecule(molecule):
        add_command(f'CONNECT {molecule}')

    def make(id):
        add_command(f'CONNECT {id}')

    def get_sample():
        add_command('CONNECT 2')


class Player:
    def __init__(self, id):
        self.id = id
        self.target = None
        self.eta = 0
        self.score = 0
        self.storage = dict(MOLECULES_DICT)
        self.expertise = dict(MOLECULES_DICT)
        self.samples = []
        self.diagnosed_samples = []
        self.undiagnosed_samples = []

    def __repr__(self):
        return f'Player {self.id} At {self.target} Score: {self.score} Storage: {self.storage}'

    def update_samples(self):
        self.samples = list(filter(lambda x: x.owner == self.id, samples))
        list(map(self.update_sample_cost, self.samples))
        self.diagnosed_samples = list(filter(lambda x: x.health != NO_DATA, self.samples))
        self.undiagnosed_samples = list(filter(lambda x: x.health == NO_DATA, self.samples))

    def update_sample_cost(self, sample):
        for molecule in MOLECULES_LIST:
            sample.cost[molecule] -= self.expertise[molecule]
            if sample.cost[molecule] < 0:
                sample.cost[molecule] = 0


class Sample:
    def __init__(self):
        self.id = None
        self.owner = None
        self.rank = 0
        self.expertise_gain = ''
        self.health = 0
        self.cost = dict(MOLECULES_DICT)

    def __repr__(self):
        return f'Sample {self.id} Carried by {self.owner} Gives {self.health} Points.\nCosts: {self.cost}\n'


def debug(s):
    sys.stderr.write(f'{s}\n')


def init_projects():
    projects = []
    project_count = int(input())
    for i in range(project_count):
        projects.append(dict(zip(MOLECULES_LIST, list(map(int, input().split())))))  # ))))))))))))))))
    return projects


def add_command(command):
    command_queue.append(command)


def handle_samples():
    for _ in range(MAX_SAMPLES):
        do.get_sample()
    go.diagnosis()


def handle_diagnosis():
    if me.undiagnosed_samples:
        for sample in me.undiagnosed_samples:
            do.diagnose(sample.id)
        return
    remaining_molecules = calculate_remaining_molecules()
    best_samples = sorted(filter(lambda sample: sample.owner != ENEMY, samples), key=value_sample)[:3]
    my_worst_samples = sorted(filter(lambda sample: sample.owner == ME, samples), key=value_sample, reverse=True)
    upload_count = 0
    for sample in best_samples:
        upload_count += handle_sample_switching(sample, my_worst_samples)
    if upload_count == MAX_SAMPLES:
        go.samples()
        return
    go.molecules()
    debug(f'CHOSEN: {best_samples[0].id}')
    return best_samples[0].id


def calculate_remaining_molecules():
    cheap_enemy_samples = list(filter(lambda sample: sample.rank != 3, enemy.samples))
    for molecule in MOLECULES_LIST:
        remaining_molecules[molecule] = available_molecules[molecule] - max(
            list(map(lambda sample: sample.cost[molecule], cheap_enemy_samples)), default=0)
    return remaining_molecules


def value_sample(sample):
    for molecule in MOLECULES_LIST:
        if sample.cost[molecule] > remaining_molecules[molecule]:
            return BAD_SAMPLE
    return sum(sample.cost.values()) / sample.health


def handle_sample_switching(sample, my_worst_samples):
    upload_count = 0
    if sample.owner != ME and value_sample(sample) != BAD_SAMPLE:
        do.upload(my_worst_samples.pop(0).id)
        do.download(sample.id)
    elif sample.owner == ME and value_sample(sample) == BAD_SAMPLE:
        do.upload(sample.id)
        upload_count = 1
    return upload_count


def handle_molecules():
    required_molecules = decompress_histogram_into_str(get_my_sample(chosen_sample).cost)
    for molecule in required_molecules:
        do.collect_molecule(molecule)
    go.lab()


def handle_lab():
    do.make(chosen_sample)
    if len(me.samples) == 1:
        go.samples()
        return None
    go.molecules()
    return next(filter(lambda sample: sample.id != chosen_sample, me.samples)).id


def decompress_histogram_into_str(d):
    s = ''
    for mol in d:
        s += mol * d[mol]
    return s


def get_my_sample(id):
    my_sample = list(filter(lambda sample: sample.id == id, me.samples))
    if my_sample:
        return my_sample[0]
    return None


def get_player_input(i):
    temp = input().split()
    player = Player(i)
    player.target = temp.pop(0)
    player.eta, player.score, player.storage['A'], player.storage['B'], player.storage['C'], \
    player.storage['D'], player.storage['E'], player.expertise['A'], player.expertise['B'], \
    player.expertise['C'], player.expertise['D'], player.expertise['E'] = map(int, temp)
    return player


def get_sample_input():
    sample_count = int(input())
    samples = [Sample() for _ in range(sample_count)]
    for i in range(sample_count):
        temp = input().split()
        samples[i].expertise_gain = temp.pop(3)
        samples[i].id, samples[i].owner, samples[i].rank, samples[i].health, samples[i].cost['A'], samples[i].cost['B'], \
        samples[i].cost['C'], samples[i].cost['D'], samples[i].cost['E'] = map(int, temp)
    return samples


# defining global vars
projects = init_projects()
available_molecules = dict(MOLECULES_DICT)
command_queue = []
go.samples()
chosen_sample = None
remaining_molecules = MOLECULES_DICT

# game loop
while True:
    me = get_player_input(ME)
    enemy = get_player_input(ENEMY)
    available_molecules = dict(zip(MOLECULES_LIST, list(map(int, input().split()))))
    samples = get_sample_input()
    me.update_samples()
    enemy.update_samples()

    debug(f'MY TARGET: {me.target}')
    debug(f'ARIVING IN {me.eta} TURNS')
    debug(f'EXPERTISE: {me.expertise}')
    debug(f'MY STORAGE: {me.storage}')
    debug(f'ENEMY STORAGE: {enemy.storage}')
    debug(f'CHOSEN SAMPLE: {get_my_sample(chosen_sample)}')
    debug(f'MY SAMPLES: {me.samples}')

    if me.eta > 0:
        print('WAIT')
        continue
    if command_queue:
        pass
    elif me.target == 'SAMPLES':
        handle_samples()
        debug('------1------')
    elif me.target == 'DIAGNOSIS':
        chosen_sample = handle_diagnosis()
        debug('------2------')
    elif me.target == 'MOLECULES':
        handle_molecules()
        debug('------3------')
    elif me.target == 'LABORATORY':
        chosen_sample = handle_lab()
        debug('------4------')

    debug(f'COMMAND QUEUE: {command_queue}')

    print(command_queue.pop(0))

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr, flush=True)



