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

#While permanece rodando enquanto for insatisfázivel, se for sat retorna a resolução e encerra
while(True):
    solver = Glucose4()
    instance_mapper = SatPlanInstanceMapper()
    #Seta o estado inicial do problema
    #Mapeia os literais para enviar ao solver   
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
    
    #Seta o estado final
    #Mapeia o estado do problema ao final da action               
    def set_final_state():
        z = create_literals_for_level_from_list(
            level, sat_plan_instance.get_final_state())

        instance_mapper.add_list_of_literals_to_mapping(z)

        for final_block_state in instance_mapper.get_list_of_literals_from_mapping(z):
            solver.add_clause([final_block_state])  

    set_initial_state()
    set_final_state()
    #Estados das ações
    levels_actions_states = []    
 
    for i in range(level):
        a = create_literals_for_level_from_list(i, sat_plan_instance.get_actions())
        
        for item in a:
            levels_actions_states.append(item)
            
        instance_mapper.add_list_of_literals_to_mapping(a)
        actions_list = instance_mapper.get_list_of_literals_from_mapping(a)
        solver.add_clause(actions_list)
        
        #Cria a lógica para viajar entre a ação atual e a próxima. 
        for action in actions_list:
            for other_action in actions_list:
                if(other_action != action):
                    solver.add_clause([-action, -other_action])
                      
        #For que viaja entre as ações para criar as pré condições e pós condições
        for action in sat_plan_instance.get_actions():
            b = create_literals_for_level_from_list(
                i, sat_plan_instance.get_action_preconditions(action))
            instance_mapper.add_list_of_literals_to_mapping(b)
            
            #Pega a ação atual do nível atual para receber o valor dela no mapeamento
            level_action = f'{i}_{action}'
            level_action_value = instance_mapper.get_literal_from_mapping(level_action)

            #Salva as cláusulas das prés condições no formato (~a V b), com a sendo a ação
            for pre_condition_literal in b:
                solver.add_clause(
                    [-level_action_value, instance_mapper.get_literal_from_mapping(pre_condition_literal)])
           
            c = create_literals_for_level_from_list(
                i+1, sat_plan_instance.get_action_posconditions(action))
            instance_mapper.add_list_of_literals_to_mapping(c)

            #Salva as cláusulas das pós condições no formato (~a V c), com a sendo a ação do nível
            for post_condition_literal in c:
                solver.add_clause(
                    [-level_action_value, instance_mapper.get_literal_from_mapping(post_condition_literal)])
            
            for literal_state in sat_plan_instance.get_state_atoms():
                next_literal = create_literal_for_level(i+1, literal_state)
                current_literal = create_literal_for_level(i, literal_state)
                
                #Obtém o literal atual e o próximo e salva ambos no mapping
                if(next_literal not in c and f'~{next_literal}' not in c):
                    #Próximo literal
                    instance_mapper.add_literal_to_mapping(next_literal)
                    #Literal atual
                    instance_mapper.add_literal_to_mapping(current_literal)
                    
                    #Salva ambos no mapping
                    next_literal_value = instance_mapper.get_literal_from_mapping(next_literal)        
                    current_literal_value = instance_mapper.get_literal_from_mapping(current_literal)     
                    
                    #E adiciona eles nas cláusulas
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