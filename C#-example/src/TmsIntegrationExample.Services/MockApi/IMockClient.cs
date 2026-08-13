// <copyright file="IMockClient.cs" company="Engaged Technologies">
//      Copyright (c) Engaged Technologies. All rights reserved.
//  </copyright>
// <summary>
//     Interface for the MockClient
// </summary>

namespace TmsIntegrationExample.Services.MockApi
{
    using System.Collections.Generic;
    using System.Threading.Tasks;
    using TmsIntegrationExample.Services.MockApi.Model;

    public interface IMockClient
    {
        Task<List<Order>> GetOrdersAsync(string filePath);

        Task<Address> GetAddressByAddressIdAsync(string filePath);
    }
}
