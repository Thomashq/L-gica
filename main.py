import sys
from instance_manager.satplan_instance import SatPlanInstance, SatPlanInstanceMapper

def create_literal_for_level(level, literal):
    pure_atom = literal.replace("~","")
    return f"~{level}_{pure_atom}" if literal[0] == "~" else f"{level}_{pure_atom}"

def create_literals_for_level_from_list(level, literals):
    return [create_literal_for_level(level, literal) for literal in literals]

def create_state_from_true_atoms(true_atoms, all_atoms):
    initial_state = [f"~{atom}" for atom in all_atoms if atom not in true_atoms]
    return true_atoms + initial_state

def create_state_from_literals(literals, all_atoms):
    positive_literals = [literal for literal in literals if literal[0] != "~"]
    return create_state_from_true_atoms(positive_literals, all_atoms)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python your_script.py <filename>")
        sys.exit(1)       

    #o codigo a seguir é exemplo de uso
    satPlanInstance = SatPlanInstance(sys.argv[1])
    instanceMapper  = SatPlanInstanceMapper()
    instanceMapper.add_list_of_literals_to_mapping(satPlanInstance.get_atoms())
    print(instanceMapper.mapping)
    a = satPlanInstance.get_state_atoms()
    a = satPlanInstance.get_action_posconditions("pick-up_b")
    b = instanceMapper.get_list_of_literals_from_mapping(a)
    print(b)
    print(instanceMapper.get_literal_from_mapping_reverse(-8))
    print(create_literals_for_level_from_list(5,a))
    print(create_state_from_literals(['holding_b','on_a_b'],satPlanInstance.get_atoms()))


