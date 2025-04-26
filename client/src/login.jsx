import "bootstrap/dist/css/bootstrap.min.css";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./animate2.css";

export default function AuthPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    role: "",
    age: "",
    domain: "",
  });

  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
  
    const endpoint = isLogin ? "login" : "register";
  
    const response = await fetch(`http://localhost:5000/${endpoint}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include", // 👈 includes cookies
      body: JSON.stringify(formData),
    });
  
    const data = await response.json();
  
    if (response.ok) {
      // ✅ Save data to localStorage
      localStorage.setItem("user_email", formData.email);
      localStorage.setItem("user_name", formData.name || "User");
  
      alert(isLogin ? "Login Successful!" : "Registration Successful!");
      navigate("/");
    } else {
      alert(data.message || "Something went wrong");
    }
  };
  
  
  return (
    <div className="d-flex flex-column align-items-center justify-content-center min-vh-100 bg-light px-3">
      {/* Welcome Text */}
      <div className="text-center my-4 animate__animated animate__zoomIn">
        <h2 className="fw-bold text-dark" style={{ fontSize: "2.5rem" }}>
          👋 Welcome to <span className="text-primary">Asha AI</span>
        </h2>
      </div>

      {/* Auth Card */}
      <div
        className="col-md-6 p-5 bg-white"
        style={{
          borderRadius: "0 20px 20px 0",
          boxShadow: "0 8px 20px rgba(0, 0, 0, 0.1)",
        }}
      >
        <h2 className="fw-bold text-center text-primary mb-3">
          {isLogin ? "Log in" : "Register"}
        </h2>

        {/* Toggle Buttons */}
        <div className="d-flex justify-content-center mb-4">
          <button
            className={`btn ${isLogin ? "btn-primary" : "btn-outline-primary"} me-2 fw-bold`}
            onClick={() => setIsLogin(true)}
          >
            Login
          </button>
          <button
            className={`btn ${!isLogin ? "btn-primary" : "btn-outline-primary"} fw-bold`}
            onClick={() => setIsLogin(false)}
          >
            Register
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit}>
          {!isLogin && (
            <div className="mb-3">
              <label className="form-label">Full Name</label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                className="form-control rounded-pill shadow-sm"
                required
                placeholder="Enter your full name"
              />
            </div>
          )}

          <div className="mb-3">
            <label className="form-label">Email Address</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className="form-control rounded-pill shadow-sm"
              required
              placeholder="Enter your email"
            />
          </div>

          <div className="mb-3">
            <label className="form-label">Password</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className="form-control rounded-pill shadow-sm"
              required
              placeholder="Enter your password"
            />
          </div>

          {!isLogin && (
            <>
              <div className="mb-3">
                <label className="form-label fw-semibold">I am a</label>
                <select
                  className="form-select"
                  name="role"
                  value={formData.role}
                  onChange={handleChange}
                  required
                >
                  <option value="">Select your career stage</option>
                  <option value="Starter: Studying or recently graduated">Starter: Studying or recently graduated</option>
                  <option value="Riser: Currently working">Riser: Currently working</option>
                  <option value="Restarter: On a career break">Restarter: On a career break</option>
                </select>
              </div>

              <div className="mb-3">
                <label className="form-label fw-semibold">Age</label>
                <input
                  type="number"
                  name="age"
                  value={formData.age}
                  onChange={handleChange}
                  className="form-control"
                  required
                  placeholder="Enter your age"
                />
              </div>

              <div className="mb-3">
                <label className="form-label fw-semibold">Area of Interest / Domain</label>
                <input
                  type="text"
                  name="domain"
                  value={formData.domain}
                  onChange={handleChange}
                  className="form-control"
                  placeholder="e.g., Tech, HR, Finance"
                />
              </div>
            </>
          )}

          <button
            type="submit"
            className="btn btn-primary w-100 fw-bold rounded-pill shadow-sm"
          >
            {isLogin ? "Login" : "Sign Up"}
          </button>
        </form>

        {isLogin && (
          <p className="text-center mt-3">
            <a href="#" className="text-primary">Forgot password?</a>
          </p>
        )}
      </div>
    </div>
  );
}
