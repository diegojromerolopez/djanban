// A card spent time forecast
export class Forecast {
    id: number;
    name: string;
    model: string;
    forecaster_url: string;
    estimated_spent_time: number;
    last_update_datetime: Date;
}