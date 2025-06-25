document.getElementById('orderForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  // Get today's date in YYYY-MM-DD format
  const today = new Date().toISOString().split('T')[0];

  try {
      const response = await fetch('http://127.0.0.1:8000/predict/', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
          },
          body: JSON.stringify({ start_date: today }),
      });

      const data = await response.json();
      const forecastResult = document.getElementById('forecastResult');

      if (response.ok) {
          forecastResult.innerHTML = `<h3>Total Predicted Sales for Next 7 Days: ${data.total_predicted_sales}</h3>`;
      } else {
          forecastResult.innerHTML = `<h3>Error: ${data.detail}</h3>`;
      }
  } catch (error) {
      document.getElementById('forecastResult').innerHTML = `<h3>Failed to fetch data. Make sure the backend is running.</h3>`;
  }
});
