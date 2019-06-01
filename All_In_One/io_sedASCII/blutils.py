def get_non_basis_keys(mesh):
    key = mesh.shape_keys
    
    if key:
        key_blocks = key.key_blocks
        num_of_key_blocks = len(key_blocks)
        has_only_basis = True if num_of_key_blocks == 1 else False
        
        if not has_only_basis:
            return key_blocks[1:num_of_key_blocks]
    
    return None