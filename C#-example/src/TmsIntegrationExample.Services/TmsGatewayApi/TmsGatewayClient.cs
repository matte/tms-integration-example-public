// <copyright file="TmsGatewayClient.cs" company="Engaged Technologies">
//      Copyright (c) Engaged Technologies. All rights reserved.
//  </copyright>
// <summary>
//     Implementation of ITmsGatewayClient
// </summary>

namespace TmsIntegrationExample.Services.TmsGatewayApi
{
    using IdentityModel.Client;
    using Microsoft.Extensions.Options;
    using System.Net.Http;
    using System.Net.Http.Headers;
    using System.Net.Http.Json;
    using System.Text;
    using System.Text.Json;
    using System.Threading.Tasks;
    using TmsIntegrationExample.Services.AccessToken;
    using TmsIntegrationExample.Services.TmsGatewayApi.Configuration;
    using TmsIntegrationExample.Services.TmsGatewayApi.Model;

    public class TmsGatewayClient : ITmsGatewayClient
    {
        private readonly JsonSerializerOptions jsonSerializerOptions;
        private readonly IHttpClientFactory httpClientFactory;
        private readonly TmsGatewayConfiguration tmsGatewayConfiguration;
        private readonly IAccessTokenClient accessTokenClient;
        private TokenResponse tokenResponse;

        public TmsGatewayClient(
            IHttpClientFactory httpClientFactory,
            IOptions<TmsGatewayConfiguration> tmsGatewayConfiguration,
            JsonSerializerOptions jsonSerializerOptions,
            IAccessTokenClient accessTokenClient)
        {
            this.tmsGatewayConfiguration = tmsGatewayConfiguration.Value;
            this.httpClientFactory = httpClientFactory;
            this.jsonSerializerOptions = jsonSerializerOptions;
            this.accessTokenClient = accessTokenClient;
        }

        public static string HttpClientName => nameof(TmsGatewayClient);

        public async Task<Shipment> PostShipmentAsync(ShipmentPost shipment)
        {
            this.tokenResponse = await this.accessTokenClient.GetAccessTokenAsync();
            var httpClient = this.httpClientFactory.CreateClient(HttpClientName);
            httpClient.DefaultRequestHeaders.Clear();
            httpClient.DefaultRequestHeaders.Add("Authorization", "Bearer " + this.tokenResponse.AccessToken);
            httpClient.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));

            var jsonContent = JsonSerializer.Serialize(shipment);
            var contentString = new StringContent(jsonContent, Encoding.UTF8, "application/json");
            HttpResponseMessage response = await httpClient.PostAsync($"{this.tmsGatewayConfiguration.ShipmentsSubPath}", contentString);
            response.EnsureSuccessStatusCode();
            return await response.Content.ReadFromJsonAsync<Shipment>(this.jsonSerializerOptions);
        }
    }
}
