import sys
import math
import string
from functools import reduce

ME = 0
ENEMY = 1
NO_DATA = -1
MOLECULES_LIST = list(string.ascii_uppercase[:5])
MOLECULES_DICT = dict(zip(MOLECULES_LIST, [0] * 5))
MAX_SAMPLES = 3
MAX_MOLECULES = 10
BAD_SAMPLE = 10

MOLECULES = 'MOLECULES'
LABORATORY = 'LABORATORY'
DIAGNOSIS = 'DIAGNOSIS'
SAMPLES = 'SAMPLES'


# TODO: go(LABORATORY)
class go:
    def samples():
        add_command(f'GOTO  {SAMPLES}')

    def diagnosis():
        add_command(f'GOTO  {DIAGNOSIS}')

    def molecules():
        add_command(f'GOTO {MOLECULES}')

    def lab():
        add_command(f'GOTO {LABORATORY}')


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

    def get_sample(rank):
        add_command(f'CONNECT {rank}')

    def wait():
        add_command('WAIT')


def get_distance(first_location, second_location):
    if first_location == second_location:
        return 0
    if {first_location, second_location} == {MOLECULES, DIAGNOSIS}:
        return 4
    return 3


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
        # for sample in self.samples:
        #    self.update_sample_cost(sample)
        self.diagnosed_samples = list(filter(lambda x: x.health != NO_DATA, self.samples))
        self.undiagnosed_samples = list(filter(lambda x: x.health == NO_DATA, self.samples))


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

    def update_sample_cost(self):
        for molecule in MOLECULES_LIST:
            if self.owner == ENEMY:
                self.cost[molecule] -= enemy.expertise[molecule]
            else:
                self.cost[molecule] -= me.expertise[molecule]

            self.cost[molecule] = max(self.cost[molecule], 0)


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
    sample_type = 3 if should_take_type_3() else 2

    for _ in range(MAX_SAMPLES):
        do.get_sample(sample_type)

    go.diagnosis()


def should_take_type_3():
    return sum(me.expertise.values()) >= 5


def is_all_samples_bad():
    all_samples = list(filter(lambda sample: sample.owner != ENEMY, samples))
    return reduce(lambda x, sample: x and get_sample_value(sample) == BAD_SAMPLE, all_samples)


def upload_all_samples():
    for sample in me.samples:
        do.upload(sample.id)


def handle_diagnosis():
    if me.undiagnosed_samples:
        for sample in me.undiagnosed_samples:
            do.diagnose(sample.id)
        return

    if is_all_samples_bad():
        upload_all_samples()
        go.samples()
        return

    best_samples = sorted(filter(lambda sample: sample.owner != ENEMY, samples), key=get_sample_value)[:3]
    my_worst_samples = sorted([sample for sample in me.samples if sample not in best_samples], key=get_sample_value,
                              reverse=True)
    samples_count = len(me.samples)
    for sample in best_samples:
        samples_count -= handle_sample_switching(sample, my_worst_samples)
    if not samples_count or not me.samples:
        go.samples()
        return
    go.molecules()


def calculate_available_molecules():
    all_available_molecules = dict(MOLECULES_DICT)
    for molecule in MOLECULES_LIST:
        all_available_molecules[molecule] = available_molecules[molecule] + me.storage[molecule]
    return all_available_molecules


def get_enemy_eta_to_molecules():
    return get_distance(enemy.target, MOLECULES) + enemy.eta


def get_potentially_stolen_molecules(molecules_left_for_sample_completion):
    return max(molecules_left_for_sample_completion - get_enemy_eta_to_molecules(), 0)


def get_stealing_penalty(sample_cost, steal_threshold):
    penalty = 0
    for molecule in MOLECULES_LIST:
        effective_cost = sample_cost[molecule] - me.storage[molecule]
        penalty += max(effective_cost - steal_threshold, 0)
    return penalty


def get_molecules_left_for_sample_completion(sample):
    molecules_left_dict = dict(sample.cost)
    for molecule in MOLECULES_LIST:
        molecules_left_dict[molecule] = max(molecules_left_dict[molecule] - me.storage[molecule], 0)
    return sum(molecules_left_dict.values())


def get_sample_value(sample):
    remaining_molecules = calculate_available_molecules()
    molecules_left_for_sample_completion = get_molecules_left_for_sample_completion(sample)

    if molecules_left_for_sample_completion + sum(me.storage.values()) > MAX_MOLECULES:
        return BAD_SAMPLE

    for molecule in MOLECULES_LIST:
        if sample.cost[molecule] > remaining_molecules[molecule]:
            return BAD_SAMPLE

    steal_threshold = get_potentially_stolen_molecules(molecules_left_for_sample_completion)
    steal_penalty = get_stealing_penalty(sample.cost, steal_threshold) ** 0.2

    return (molecules_left_for_sample_completion ** 0.5 + steal_penalty) / sample.health


def handle_sample_switching(sample, my_worst_samples):
    upload_count = 0
    if sample.owner != ME and get_sample_value(sample) != BAD_SAMPLE:
        if my_worst_samples:
            do.upload(my_worst_samples.pop(0).id)
            do.download(sample.id)
        else:
            do.download(sample.id)
            upload_count = -1

    return upload_count


def handle_molecules():
    chosen_sample = choose_best_sample()
    if is_sample_ready(chosen_sample):
        go.lab()
        do.make(chosen_sample.id)
        return

    if get_sample_value(chosen_sample) == BAD_SAMPLE:
        go.diagnosis()
        return

    do.collect_molecule(choose_next_molecule(chosen_sample))


def is_sample_ready(sample):
    return choose_next_molecule(sample) is None


def choose_next_molecule(sample):
    required_molecules = dict(sample.cost)
    for molecule in MOLECULES_LIST:
        required_molecules[molecule] = max(required_molecules[molecule] - me.storage[molecule], 0)

    required_molecules_str = decompress_histogram_into_list(required_molecules)
    if not required_molecules_str:
        return None
    # TODO: choose molecule based on risk level
    return required_molecules_str[0]


def print_interesting_debug_case():
    try:
        prechosen_sample = int(command_queue[0].split()[1])
        if choose_best_sample().id != prechosen_sample:
            debug(f'Interesting: while walking towards lab, a different sample became better')
    except:
        pass


def handle_lab():
    print_interesting_debug_case()
    if not me.samples:
        go.samples()
        return

    if get_sample_value(choose_best_sample()) == BAD_SAMPLE:
        go.diagnosis()
        return
    go.molecules()


def decompress_histogram_into_list(d):
    s = []
    for mol in d:
        s += mol * d[mol]
    return s


def get_my_sample(id):
    my_sample = list(filter(lambda sample: sample.id == id, me.samples))
    if my_sample:
        return my_sample[0]
    return None


def choose_best_sample():
    if not me.samples:
        return "There are no samples"
    return min(me.samples, key=get_sample_value)


def get_player_input(id):
    raw_input = input().split()
    player = Player(id)
    player.target = raw_input.pop(0)
    player.eta, player.score, player.storage['A'], player.storage['B'], player.storage['C'], \
    player.storage['D'], player.storage['E'], player.expertise['A'], player.expertise['B'], \
    player.expertise['C'], player.expertise['D'], player.expertise['E'] = map(int, raw_input)
    return player


def get_sample_input():
    sample_count = int(input())
    samples = [Sample() for _ in range(sample_count)]
    for i in range(sample_count):
        raw_input = input().split()
        samples[i].expertise_gain = raw_input.pop(3)
        samples[i].id, samples[i].owner, samples[i].rank, samples[i].health, samples[i].cost['A'], samples[i].cost['B'], \
        samples[i].cost['C'], samples[i].cost['D'], samples[i].cost['E'] = map(int, raw_input)
    return samples


# defining global vars
projects = init_projects()
available_molecules = dict(MOLECULES_DICT)
command_queue = []
go.samples()
required_molecules_queue = ''

# game loop
while True:
    me = get_player_input(ME)
    enemy = get_player_input(ENEMY)
    available_molecules = dict(zip(MOLECULES_LIST, list(map(int, input().split()))))
    samples = get_sample_input()
    for sample in samples:
        sample.update_sample_cost()
    me.update_samples()
    enemy.update_samples()

    debug(f'MY TARGET: {me.target}')
    debug(f'ARIVING IN {me.eta} TURNS')
    debug(f'EXPERTISE: {me.expertise}')
    debug(f'MY STORAGE: {me.storage}')
    debug(f'ENEMY STORAGE: {enemy.storage}')
    debug(f'CHOSEN SAMPLE: {choose_best_sample()}')
    debug(f'MY SAMPLES: {me.samples}')

    if me.eta > 0:
        print('WAIT')
        continue
    if command_queue:
        pass
    elif me.target == SAMPLES:
        handle_samples()
        debug('------1------')
    elif me.target == DIAGNOSIS:
        handle_diagnosis()
        debug('------2------')
    elif me.target == MOLECULES:
        handle_molecules()
        debug('------3------')
    elif me.target == LABORATORY:
        handle_lab()
        debug('------4------')

    debug(f'COMMAND QUEUE: {command_queue}')

    print(command_queue.pop(0))
