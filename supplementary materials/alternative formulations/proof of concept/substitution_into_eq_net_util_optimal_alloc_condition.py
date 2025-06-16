from sympy import symbols, Eq, log, solve

# Define symbols
y, d_prime, xi, k = symbols('y d_prime xi k')
U_net = y * (1 - d_prime / (y * xi)) + (d_prime / xi) * log(d_prime / (y * xi))

# Express y_under and y_over in terms of y and k
y_under = y * (1 - k)
y_over = y * (1 + k)

# Substitute y_under and y_over into the U_net equation
U_net_under = U_net.subs(y, y_under).simplify()
U_net_over = U_net.subs(y, y_over).simplify()

# Compute the percentage errors from U_net for y_under and y_over
error_under = (U_net - U_net_under) / U_net
error_over = (U_net_over - U_net) / U_net

# Set the percentage errors equal
equation = Eq(error_under, error_over)

# Simplify the equation
simplified_equation = equation.simplify()

print(simplified_equation)

