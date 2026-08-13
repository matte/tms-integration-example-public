// <copyright file="MockClient.cs" company="Engaged Technologies">
//      Copyright (c) Engaged Technologies. All rights reserved.
//  </copyright>
// <summary>
//     Implementation of IMockClient
// </summary>

namespace TmsIntegrationExample.Services.MockApi
{
    using System.Collections.Generic;
    using System.IO;
    using System.Text.Json;
    using System.Threading.Tasks;
    using TmsIntegrationExample.Services.MockApi.Model;

    public class MockClient : IMockClient
    {
        public async Task<List<Order>> GetOrdersAsync(string filePath)
        {
            using FileStream stream = File.OpenRead(filePath);
            return await JsonSerializer.DeserializeAsync<List<Order>>(stream);
        }

        public async Task<Address> GetAddressByAddressIdAsync(string filePath)
        {
            using FileStream stream = File.OpenRead(filePath);
            return await JsonSerializer.DeserializeAsync<Address>(stream);
        }
    }
}
