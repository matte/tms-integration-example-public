// <copyright file="MockProcessor.cs" company="Engaged Technologies">
//      Copyright (c) Engaged Technologies. All rights reserved.
//  </copyright>
// <summary>
//     implementation class for processing Mock orders/shipments
// </summary>

namespace TmsIntegrationExample.Example
{
    using Microsoft.Extensions.Options;
    using System.Threading.Tasks;
    using TmsIntegrationExample.Example.Extensions;
    using TmsIntegrationExample.Example.Transformers;
    using TmsIntegrationExample.Services.MockApi;
    using TmsIntegrationExample.Services.TmsGatewayApi;
    using TmsIntegrationExample.Services.TmsGatewayApi.Configuration;

    public class TmsIntegrationExampleProcessor : ITmsIntegrationExampleProcessor
    {
        private readonly ITmsGatewayClient tmsGatewayClient;
        private readonly IMockClient mockClient;
        private readonly TmsGatewayConfiguration tmsGatewayConfiguration;

        public TmsIntegrationExampleProcessor(
            ITmsGatewayClient tmsGatewayClient, 
            IMockClient mockClient,
            IOptions<TmsGatewayConfiguration> tmsGatewayConfiguration)
        {
            this.tmsGatewayConfiguration = tmsGatewayConfiguration.Value;
            this.tmsGatewayClient = tmsGatewayClient;
            this.mockClient = mockClient;
        }

        public async Task<int> ProcessAsync()
        {
            var ordersResult = await this.mockClient.GetOrdersAsync(@"MockApi\Orders.json".PathFromExecutingAssemblyLocation());

            if (ordersResult != null)
            {
                foreach (var order in ordersResult)
                {
                    var sourceLocation = await this.mockClient.GetAddressByAddressIdAsync(@"MockApi\SourceLocation.json".PathFromExecutingAssemblyLocation());
                    var shipTo = new Services.MockApi.Model.Address();
                    if (order.ShipToId != null)
                    {
                        shipTo = await this.mockClient.GetAddressByAddressIdAsync(@"MockApi\ShipTo.json".PathFromExecutingAssemblyLocation());
                    }

                    var shipmentPost = new MockOrderToShipment().Transform(order, shipTo, sourceLocation, this.tmsGatewayConfiguration.AccountNumber);

                    await this.tmsGatewayClient.PostShipmentAsync(shipmentPost);
                }
            }

            return ordersResult.Count;
        }
    }
}
