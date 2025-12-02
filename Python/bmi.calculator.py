def calculate_bmi(weight,height):
    bmi = weight/height**2
    return bmi
if __name__ == "__main__":
    weight = float(input("Enter your weight in kilograms:"))
    height = float(input("Enter your height in meters:"))

bmi = calculate_bmi(weight,height)
if bmi < 18.5:
   print("Underweight")
elif 18.5 <= bmi < 25:
   print("Normal weight")
elif 25 <= bmi <30:
   print("Overweight")
else:
   print("Obese")