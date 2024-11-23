import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const Private = () => {
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const fetchPrivate = async () => {
      const response = await fetch(`${process.env.BACKEND_URL}/api/private`, {
        headers: {
          Authorization: `Bearer ${sessionStorage.getItem("token")}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setMessage(data.msg);
      } else {
        sessionStorage.removeItem("token");
        navigate("/login");
      }
    };

    fetchPrivate();
  }, [navigate]);

  return <h2>{message || "Loading..."}</h2>;
};

export default Private;
