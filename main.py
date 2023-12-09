import sys
from pysat.solvers import Glucose4
from instance_manager.satplan_instance import SatPlanInstance, SatPlanInstanceMapper

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

sat_plan_instance = SatPlanInstance(sys.argv[1])
level = 1

while(True):
    solver = Glucose4()
    instance_mapper = SatPlanInstanceMapper()
    def set_initial_state():
        y = create_literals_for_level_from_list(0, sat_plan_instance.get_initial_state())

        instance_mapper.add_list_of_literals_to_mapping(y)

        for initial_block_state in instance_mapper.get_list_of_literals_from_mapping(y):
            solver.add_clause([initial_block_state])
        
        states = create_literals_for_level_from_list(0, sat_plan_instance.get_state_atoms())
        for state in states:
            if(state not in y):
                instance_mapper.add_literal_to_mapping(state)
                state_value = instance_mapper.get_literal_from_mapping(state)
                solver.add_clause([-state_value])
                
    def set_final_state():
        z = create_literals_for_level_from_list(
            level, sat_plan_instance.get_final_state())

        instance_mapper.add_list_of_literals_to_mapping(z)

        for final_block_state in instance_mapper.get_list_of_literals_from_mapping(z):
            solver.add_clause([final_block_state])  
    # Mapeia as ações de pré condição e pós condição
    set_initial_state()
    set_final_state()
    levels_actions_states = []    

    for i in range(level):
        a = create_literals_for_level_from_list(i, sat_plan_instance.get_actions())
        
        for item in a:
            levels_actions_states.append(item)
            
        instance_mapper.add_list_of_literals_to_mapping(a)
        actions_list = instance_mapper.get_list_of_literals_from_mapping(a)
        solver.add_clause(actions_list)
        
        for action in actions_list:
            for other_action in actions_list:
                if(other_action != action):
                    solver.add_clause([-action, -other_action])  
        
        for action in sat_plan_instance.get_actions():
            b = create_literals_for_level_from_list(
                i, sat_plan_instance.get_action_preconditions(action))
            instance_mapper.add_list_of_literals_to_mapping(b)
            
            level_action = f'{i}_{action}'
            level_action_value = instance_mapper.get_literal_from_mapping(level_action)

            for pre_condition_literal in b:
                solver.add_clause(
                    [-level_action_value, instance_mapper.get_literal_from_mapping(pre_condition_literal)])

            c = create_literals_for_level_from_list(
                i+1, sat_plan_instance.get_action_posconditions(action))
            instance_mapper.add_list_of_literals_to_mapping(c)

            for post_condition_literal in c:
                solver.add_clause(
                    [-level_action_value, instance_mapper.get_literal_from_mapping(post_condition_literal)])
            
            for literal_state in sat_plan_instance.get_state_atoms():
                next_literal = create_literal_for_level(i+1, literal_state)
                current_literal = create_literal_for_level(i, literal_state)
                
                if(next_literal not in c and f'~{next_literal}' not in c):
                    instance_mapper.add_literal_to_mapping(next_literal)
                    instance_mapper.add_literal_to_mapping(current_literal)
                    
                    next_literal_value = instance_mapper.get_literal_from_mapping(next_literal)        
                    current_literal_value = instance_mapper.get_literal_from_mapping(current_literal)     
                    
                    solver.add_clause(
                    [-level_action_value, -current_literal_value, next_literal_value])
                    
                    solver.add_clause(
                    [-level_action_value, current_literal_value, -next_literal_value])                

    is_satisfiable = solver.solve()
        # Pega o caminho usado para resolver
    if is_satisfiable:
        print(f'Nível {i+1} é Satisfazível: ')
        model = solver.get_model()
        path_string = ' '.join(map(str, model))
        actions_names = instance_mapper.get_list_of_literals_from_mapping_reverse(
            model)
        for action_name in actions_names:
            if(action_name in levels_actions_states):
                print(action_name)
        break
    else:
        print(f'Nível {i+1} Insatisfazível: ')
        level += 1