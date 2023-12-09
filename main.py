import sys
from pysat.solvers import Glucose4
from pysat.formula import CNF
from instance_manager.satplan_instance import SatPlanInstance, SatPlanInstanceMapper

solver = Glucose4()
sat_plan_instance = SatPlanInstance(sys.argv[1])
instance_mapper = SatPlanInstanceMapper()
instance_mapper.add_list_of_literals_to_mapping(sat_plan_instance.get_atoms())


def create_literal_for_level(level, literal):
    pure_atom = literal.replace("~", "")
    return f"~{level}_{pure_atom}" if literal[0] == "~" else f"{level}_{pure_atom}"


def create_literals_for_level_from_list(level, literals):
    return [create_literal_for_level(level, literal) for literal in literals]


def create_state_from_true_atoms(true_atoms, all_atoms):
    initial_state = [
        f"~{atom}" for atom in all_atoms if atom not in true_atoms]
    return true_atoms + initial_state


def create_state_from_literals(literals, all_atoms):
    positive_literals = [literal for literal in literals if literal[0] != "~"]
    return create_state_from_true_atoms(positive_literals, all_atoms)

# Retorna o tanto de ações necessárias para resolver o problema


def level_counter():
    actions_list = sat_plan_instance.get_actions()
    n_level = len(actions_list)

    return n_level

# Estado inicial: Mapeia as pré-condições das ações.


def set_initial_state():
    y = create_literals_for_level_from_list(0, sat_plan_instance.get_initial_state())

    instance_mapper.add_list_of_literals_to_mapping(y)

    for initial_block_state in instance_mapper.get_list_of_literals_from_mapping(y):
        # Corrigido para usar uma lista
        solver.add_clause([initial_block_state])

    states = create_literal_for_level(0 ,sat_plan_instance.get_state_atoms())
    
# Estado final: Como os blocos devem estar após as ações.


def set_final_state():
    level = level_counter()
    # print(f'Final State:{sat_plan_instance.get_final_state()}')

    z = create_literals_for_level_from_list(
        level, sat_plan_instance.get_final_state())
    # print(z)

    instance_mapper.add_list_of_literals_to_mapping(z)

    for final_block_state in instance_mapper.get_list_of_literals_from_mapping(z):
        solver.add_clause([final_block_state])  # Corrigido para usar uma lista


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python main.py blocks-4-0.strips")
        sys.exit(1)

    # o codigo a seguir é exemplo de uso
    satPlanInstance = SatPlanInstance(sys.argv[1])
    instanceMapper = SatPlanInstanceMapper()
    instanceMapper.add_list_of_literals_to_mapping(satPlanInstance.get_atoms())
    # print(instanceMapper.mapping)
    a = satPlanInstance.get_state_atoms()
    a = satPlanInstance.get_action_posconditions("pick-up_b")
    b = instanceMapper.get_list_of_literals_from_mapping(a)
    # print(b)
    # print(instanceMapper.get_literal_from_mapping_reverse(-8))
    # print(create_literals_for_level_from_list(5,a))
    # print(create_state_from_literals(['holding_b','on_a_b'],satPlanInstance.get_atoms()))

# Pega a quantidade de ações(TODAS AS AÇÕES, e não ação por ação separadamente) e usa para contar quantos passos tem para chegar ao final do problema
n_level = level_counter()

# Mapeia as ações de pré condição e pós condição
for i in range(n_level):
    a = create_literals_for_level_from_list(i, sat_plan_instance.get_actions())

    instance_mapper.add_list_of_literals_to_mapping(a)
    actions_list = instance_mapper.get_list_of_literals_from_mapping(a)
    set_initial_state()
    set_final_state()

    for action in sat_plan_instance.get_actions():
        b = create_literals_for_level_from_list(
            i, sat_plan_instance.get_action_preconditions(action))
        instance_mapper.add_list_of_literals_to_mapping(b)

        action_literal = instance_mapper.get_literal_from_mapping(action)

        for pre_condition_literal in b:
            solver.add_clause(
                [-action_literal, instance_mapper.get_literal_from_mapping(pre_condition_literal)])

        c = create_literals_for_level_from_list(
            i+1, sat_plan_instance.get_action_posconditions(action))
        instance_mapper.add_list_of_literals_to_mapping(c)

        for post_condition_literal in c:
            solver.add_clause(
                [-action_literal, instance_mapper.get_literal_from_mapping(post_condition_literal)])

    unaffected_states = [
        state for state in sat_plan_instance.get_state_atoms() if state not in b]
    unaffected_literals = create_literals_for_level_from_list(
        i, unaffected_states)
    unaffected_literals_mapped = instance_mapper.get_list_of_literals_from_mapping(
        unaffected_literals)

    for unaffected_literal in unaffected_literals_mapped:
        solver.add_clause(
            [-instance_mapper.get_literal_from_mapping(action), -unaffected_literal])

        is_satisfiable = solver.solve()
    # Pega o caminho usado para resolver
        if is_satisfiable:
            model = solver.get_model()
            path_string = ' '.join(map(str, model))
            actions_names = instance_mapper.get_list_of_literals_from_mapping_reverse(
                model)
            #print(f'Nivel {i} Caminho da solução: {actions_names}\n')
            print(f'{model}') 
            break
        else:
            print(f'Nível {i} Insatisfazível')