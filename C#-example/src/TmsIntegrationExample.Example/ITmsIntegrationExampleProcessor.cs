// <copyright file="IMockProcessor.cs" company="Engaged Technologies">
//      Copyright (c) Engaged Technologies. All rights reserved.
//  </copyright>
// <summary>
//     Job to pull orders/shipments
// </summary>

namespace TmsIntegrationExample.Example
{
    using System.Threading.Tasks;

    public interface ITmsIntegrationExampleProcessor
    {
        Task<int> ProcessAsync();
    }
}
