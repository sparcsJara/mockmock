from instrumentation import instrument
from mockGenerator import mockGenerator

num_branches, branches, pdg_class, pdg_methods = instrument('cat_owner.py')

gen = mockGenerator('cat_owner.py', 'test_cat_owner.py', 'cat_database.CatDatabase')
print(gen.run([1,2]))