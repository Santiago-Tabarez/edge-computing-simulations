import numpy as np

# Define the net utility function
def U_net(y, xi, d_prime):
    return y * (1 - d_prime / (y * xi)) + (d_prime / xi) * np.log(d_prime / (y * xi))

# Gradient functions
def dU_dy(y, xi, d_prime):
    A = d_prime / (y * xi)
    return 1 - A

def dU_dxi(y, xi, d_prime):
    A = d_prime / (y * xi)
    return - (d_prime / xi**2 ) * np.log(A)

# Define the critical value for xi where U_net has a maximum
def critical_xi(y, d_prime):
    return d_prime / (y * np.exp(1))  # xi = d' / (y * e)

# Define a function to ensure the constraints d' < y * xi and xi > critical_xi
def project_condition(y, xi, d_prime):
    xi_critical = critical_xi(y, d_prime)
    if d_prime >= y * xi:
        xi = d_prime / y + 1e-6  # Ensure d' < y * xi
    if xi <= xi_critical:
        xi = xi_critical + 1e-6  # Ensure xi > critical_xi
    return y, xi

# Define the projection function to ensure y and xi remain positive
def project_positive(value, min_value):
    return max(value, min_value)

# Main function to find y and xi that make U_net(y, xi, d_prime) equal to target_value
def find_y_xi_for_U_net(target_value, y_init=0.5, xi_init=0.1, alpha=0.001, tolerance=1e-6, max_iterations=10000):
    # Gradient Descent parameters with an additional constraint
    y = y_init  # Initial guess for y (must stay positive)
    xi = xi_init  # Initial guess for xi (must stay positive)
    d_prime = 0.5 / (365 * 3 * 96)  # d' value

    # Minimum allowed value to ensure y and xi remain positive
    min_y = 1e-6
    min_xi = 1e-6

    # Gradient Descent loop to minimize |U_net(y, xi, d_prime) - target_value| with positive constraints and additional condition
    for i in range(max_iterations):
        U_value = U_net(y, xi, d_prime)

        # Compute the error
        error = U_value - target_value

        # Check if U_net is close enough to target_value
        if abs(error) < tolerance:
            print(f'Found U_net = {target_value} at iteration {i + 1}.')
            break

        # Compute the gradients
        grad_y = dU_dy(y, xi, d_prime)
        grad_xi = dU_dxi(y, xi, d_prime)

        # Update y and xi using the gradients
        y_new = y - alpha * error * grad_y  # Adjust y
        xi_new = xi - alpha * error * grad_xi  # Adjust xi

        # Project y and xi to remain positive
        y = project_positive(y_new, min_y)
        xi = project_positive(xi_new, min_xi)

        # Ensure the condition d' < y * xi and xi > critical_xi is satisfied
        y, xi = project_condition(y, xi, d_prime)

        if i % 100 == 0:  # Print every 100 iterations for tracking progress
            print(f'Iteration {i + 1}, y: {y}, xi: {xi}, U_net(y, xi) = {U_net(y, xi, d_prime)}')

    else:
        print('Maximum iterations reached without convergence.')

    # Final values after the loop
    print(f'Optimal y: {y}, Optimal xi: {xi}, Final U_net(y, xi) = {U_net(y, xi, d_prime)}')

    return y, xi

# Example usage:
target_value = float(input("Enter the target value for U_net: "))
find_y_xi_for_U_net(target_value)
