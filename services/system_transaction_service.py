import random

class SystemTransactionService:
    """Service to generate realistic transaction patterns"""
    
    def generate_transactions(self, count=5):
        """Generate realistic transactions based on common patterns"""
        transaction_types = ['general', 'transfer', 'update']
        transactions = []
        
        for i in range(count):
            # Weighted random selection - more general transactions
            trans_type = random.choices(
                transaction_types,
                weights=[0.5, 0.3, 0.2],
                k=1
            )[0]
            
            transactions.append({
                'type': trans_type,
                'process_id': None  # Will be assigned if linked to a process
            })
        
        return transactions
    
    def generate_transaction_operations(self, transaction_count=5):
        """Generate a sequence of realistic transaction operations"""
        operations = []
        data_items = ['A', 'B', 'C', 'D']
        
        for i in range(transaction_count):
            # Alternate between read and write operations
            op_type = 'read' if i % 2 == 0 else 'write'
            data_item = random.choice(data_items)
            
            operations.append({
                'operation': op_type,
                'data_item': data_item,
                'new_value': random.randint(50, 500) if op_type == 'write' else None
            })
        
        return operations
