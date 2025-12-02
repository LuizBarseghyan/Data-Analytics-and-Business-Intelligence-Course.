
income = float(input("Enter your monthly income:"))
expenses = float(input("Enter your monthly expenses:"))

savings = income - expenses
if savings > 0.2 * income:
   print("You are saving enough!")
else:
   print("You need to save more")

if savings > 0:
   print("You are saving not too bad)")
else:
   print ("No savings no trips")