import React, { useEffect, useState } from 'react'
import '../App.css';

export default function AppStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null)

	const getStats = () => {
	
        fetch(`http://acit3855-will.westus2.cloudapp.azure.com:processing/orders/get_stats`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received Stats")
                setStats(result);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }
    useEffect(() => {
		const interval = setInterval(() => getStats(), 2000); // Update every 2 seconds
		return() => clearInterval(interval);
    }, [getStats]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        return(
            <div>
                <h1>Latest Stats</h1>
                <table className={"StatsTable"}>
					<tbody>
						<tr>
							<th>Movie Order</th>
							<th>Payment</th>
						</tr>
						<tr>
							<td># Movie Orders: {stats['num_movie_orders']}</td>
							<td># Payments: {stats['num_payments']}</td>
						</tr>
						<tr>
							<td colspan="2">Total Movie Price {stats['sum_movie_price']}</td>
						</tr>
						<tr>
							<td colspan="2">Average Movie Price {stats['avg_movie_price']}</td>
						</tr>
					</tbody>
                </table>
                <h3>Last Updated: {stats['timestamp']}</h3>

            </div>
        )
    }
}
